import re
from typing import Optional, Tuple
import phonenumbers

# Country code ISO to dial prefix mapping
COUNTRY_ALPHA_TO_DEFAULT_REGION = {
    "CMR": "CM",
    "NGA": "NG",
    "KEN": "KE",
    "GHA": "GH"
}

def normalize_email(raw_email: str) -> Optional[str]:
    """Cleans and standardizes email addresses."""
    if not raw_email or "@" not in raw_email:
        return None
    cleaned = raw_email.strip().lower()
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", cleaned)
    return match.group(0) if match else None

def normalize_phone(raw_phone: str, country_code: str) -> Optional[Tuple[str, str]]:
    """
    Normalizes phone numbers to strict E.164 format (+237..., +234..., +254...).
    Returns (normalized_e164, inferred_country_alpha).
    """
    if not raw_phone:
        return None

    # Strip extraneous text, leaving digits and plus
    cleaned = re.sub(r"[^\d+]", "", raw_phone)
    if len(cleaned) < 8:
        return None

    region = COUNTRY_ALPHA_TO_DEFAULT_REGION.get(country_code.upper(), "NG")

    try:
        parsed = phonenumbers.parse(cleaned, region)
        if phonenumbers.is_valid_number(parsed):
            e164_val = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            # Infer country from country code
            country_iso = country_code.upper()
            if e164_val.startswith("+237"):
                country_iso = "CMR"
            elif e164_val.startswith("+234"):
                country_iso = "NGA"
            elif e164_val.startswith("+254"):
                country_iso = "KEN"
            return (e164_val, country_iso)
    except phonenumbers.NumberParseException:
        pass

    # Heuristic fallback for common African local formats
    digits = re.sub(r"\D", "", raw_phone)
    if country_code.upper() == "CMR":
        # Cameroon mobile numbers are 9 digits, starting with 6
        if len(digits) == 9 and digits.startswith("6"):
            return (f"+237{digits}", "CMR")
        elif len(digits) == 12 and digits.startswith("2376"):
            return (f"+{digits}", "CMR")
    elif country_code.upper() == "NGA":
        # Nigeria local mobile numbers: 080..., 070..., 090... (11 digits)
        if len(digits) == 11 and digits.startswith("0"):
            return (f"+234{digits[1:]}", "NGA")
        elif len(digits) == 13 and digits.startswith("234"):
            return (f"+{digits}", "NGA")
    elif country_code.upper() == "KEN":
        # Kenya mobile numbers: 07..., 01... (10 digits)
        if len(digits) == 10 and digits.startswith("0"):
            return (f"+254{digits[1:]}", "KEN")
        elif len(digits) == 12 and digits.startswith("254"):
            return (f"+{digits}", "KEN")

    return None

def extract_contacts_from_text(text: str, country_code: str) -> list[dict]:
    """
    Extracts raw phone numbers and emails found in job descriptions.
    """
    results = []
    if not text:
        return results

    # Email pattern
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    for email in re.findall(email_pattern, text):
        results.append({"raw_value": email, "contact_type": "EMAIL"})

    # Phone patterns
    phone_pattern = r"(?:\+?\d{1,3}[ -]?)?(?:(?:\(?\d{2,4}\)?[ -]?)?\d{3,4}[ -]?\d{3,4})"
    for match in re.findall(phone_pattern, text):
        clean_match = match.strip()
        # Verify it has enough digits to be a phone number
        if sum(c.isdigit() for c in clean_match) >= 8:
            results.append({"raw_value": clean_match, "contact_type": "PHONE"})

    return results
