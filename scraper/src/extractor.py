"""
Contact Extractor & African Job Scam Risk Scoring Engine.
Extracts phone numbers, WhatsApp lines, and emails via regular expressions,
normalizes them using the phonenumbers library (E.164), and calculates
explainable scam risk signals (upfront fee solicitation, free webmails, etc.).
"""

import re
from typing import List, Dict, Any, Tuple, Optional
import phonenumbers

EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,4}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}(?:[\s.-]?\d{2,4})?")

# African Scam Keywords & Weights
SCAM_INDICATORS = [
    # Fees (High Risk)
    ("registration fee", "FEE_SOLICITATION", 25, "Demande de frais d'inscription ou d'enregistrement"),
    ("training kit", "FEE_SOLICITATION", 25, "Frais obligatoires pour matériel/kit de formation"),
    ("badge fee", "FEE_SOLICITATION", 25, "Frais pour confection de badge ou carte d'accès"),
    ("application fee", "FEE_SOLICITATION", 25, "Frais de dossier de candidature"),
    ("processing fee", "FEE_SOLICITATION", 25, "Frais de traitement de dossier"),
    ("frais de dossier", "FEE_SOLICITATION", 25, "Demande illégale de frais de dossier"),
    ("frais de formation", "FEE_SOLICITATION", 25, "Frais de formation exigés avant embauche"),
    ("frais d'inscription", "FEE_SOLICITATION", 25, "Paiement requis pour valider l'inscription"),
    ("frais de badge", "FEE_SOLICITATION", 25, "Paiement pour badge d'accès"),
    ("uniform fee", "FEE_SOLICITATION", 20, "Frais d'uniforme exigés"),
    # Urgency & Suspicious Guarantees (Low-Medium Risk)
    ("urgently needed", "URGENCY_TRIGGER", 5, "Mention de recrutement ultra-urgent"),
    ("recrutement urgent", "URGENCY_TRIGGER", 5, "Formulation de recrutement urgent"),
    ("immediate employment", "URGENCY_TRIGGER", 5, "Embauche immédiate garantie sans filtre"),
    ("embauche immediate", "URGENCY_TRIGGER", 5, "Embauche immédiate sans vérification"),
    ("no experience needed", "LOW_BARRIER", 5, "Aucune expérience requise pour poste rémunéré élevé"),
    ("sans experience", "LOW_BARRIER", 5, "Sans expérience requise")
]

COUNTRY_PREFIX_MAP = {
    "237": "CMR",
    "234": "NGA",
    "254": "KEN",
    "233": "GHA"
}


def normalize_phone(raw_phone: str, default_country: str = "CMR") -> Optional[Tuple[str, str]]:
    """
    Parses and normalizes a phone number to E.164 format and returns (normalized, country_code).
    """
    cleaned = re.sub(r"[^\d+]", "", raw_phone)
    if len(cleaned) < 8:
        return None

    iso_2 = {"CMR": "CM", "NGA": "NG", "KEN": "KE", "GHA": "GH"}.get(default_country.upper(), "CM")

    try:
        parsed = phonenumbers.parse(cleaned, iso_2)
        if phonenumbers.is_possible_number(parsed):
            e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            c_code = str(parsed.country_code)
            detected_country = COUNTRY_PREFIX_MAP.get(c_code, default_country)
            return e164, detected_country
    except Exception:
        pass

    # Direct prefix matching fallback
    for pfx, ccode in COUNTRY_PREFIX_MAP.items():
        if cleaned.startswith(f"+{pfx}") or cleaned.startswith(pfx):
            return f"+{cleaned.lstrip('+')}", ccode

    return None


def extract_contacts(text: str, default_country: str = "CMR") -> List[Dict[str, str]]:
    """
    Extracts, normalizes, and deduplicates all phone numbers and emails found in text.
    """
    if not text:
        return []

    contacts = []
    seen = set()

    # Extract emails
    for match in EMAIL_REGEX.finditer(text):
        email = match.group(0).strip().lower()
        key = ("EMAIL", email)
        if key not in seen:
            seen.add(key)
            contacts.append({
                "type": "EMAIL",
                "raw": match.group(0),
                "normalized": email,
                "country": default_country
            })

    # Extract phones
    for match in PHONE_REGEX.finditer(text):
        raw_val = match.group(0).strip()
        digits = re.sub(r"\D", "", raw_val)
        if 8 <= len(digits) <= 15:
            # Avoid dates (e.g. 2026-09-23)
            if raw_val.count("-") == 2 and len(raw_val) == 10:
                continue
            norm = normalize_phone(raw_val, default_country)
            if norm:
                e164, detected_c = norm
                key = ("PHONE", e164)
                if key not in seen:
                    seen.add(key)
                    contacts.append({
                        "type": "PHONE",
                        "raw": raw_val,
                        "normalized": e164,
                        "country": detected_c
                    })

    return contacts


def infer_country_code(raw_item: Dict[str, Any], extracted_contacts: List[Dict[str, str]]) -> str:
    """
    Determines 3-letter ISO code from explicit fields, phone prefixes, or text mentions.
    """
    for k in ("country_code", "country", "location", "countryCode"):
        val = str(raw_item.get(k, "")).strip().upper()
        if val in ("CMR", "NGA", "KEN", "GHA"):
            return val
        if "CAMEROON" in val or "CAMEROUN" in val:
            return "CMR"
        if "NIGERIA" in val:
            return "NGA"
        if "KENYA" in val:
            return "KEN"
        if "GHANA" in val:
            return "GHA"

    for c in extracted_contacts:
        if c.get("type") == "PHONE" and c.get("country") in ("CMR", "NGA", "KEN", "GHA"):
            return c["country"]

    text = f"{raw_item.get('title', '')} {raw_item.get('description', '')}".lower()
    if any(k in text for k in ("douala", "yaounde", "yaoundé", "cameroun", "cameroon", "fcfa", "cfa")):
        return "CMR"
    if any(k in text for k in ("lagos", "abuja", "ikeja", "nigeria", "naira", "ngn")):
        return "NGA"
    if any(k in text for k in ("nairobi", "mombasa", "kenya", "kes", "ksh")):
        return "KEN"

    return "CMR"


def analyze_listing_risk(title: str, description: str, contacts: List[Dict[str, str]], country_code: str) -> Dict[str, Any]:
    """
    Calculates deterministic risk score (0-100) and produces human-readable signals.
    """
    combined = f"{title}\n{description}".lower()
    score = 0
    signals = []

    # Check scam indicators
    for term, code, points, explanation in SCAM_INDICATORS:
        if term in combined:
            score += points
            signals.append({
                "code": code,
                "points": points,
                "description": f"{explanation} ('{term}')"
            })

    # Check free webmail for corporate recruitment
    for c in contacts:
        if c.get("type") == "EMAIL":
            val = c.get("normalized", "")
            if any(dom in val for dom in ("@gmail.com", "@yahoo.com", "@hotmail.com", "@outlook.com")):
                score += 10
                signals.append({
                    "code": "FREE_WEBMAIL_RECRUITER",
                    "points": 10,
                    "description": f"Adresse email grand public utilisée pour un recrutement d'entreprise ({val})"
                })
                break

    # Check cross-border contact inside the single listing (e.g., Nigerian number for Cameroon ad)
    for c in contacts:
        if c.get("type") == "PHONE" and c.get("country") and c.get("country") != country_code:
            score += 35
            signals.append({
                "code": "CROSS_BORDER_CONTACT",
                "points": 35,
                "description": f"Numéro étranger ({c.get('country')}) utilisé pour une offre publiée en {country_code}"
            })
            break

    # Determine risk level
    capped_score = min(score, 100)
    if capped_score >= 70:
        level = "HIGH"
    elif capped_score >= 35:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "risk_score": capped_score,
        "risk_level": level,
        "risk_signals": signals
    }
