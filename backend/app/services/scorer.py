import json
import os
import re
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from app.models.listing import Listing
from app.models.contact import Contact
from app.models.signal import RiskSignal
from app.models.link import ListingLink

# Load scam keywords dictionary
SCAM_KEYWORDS_FILE = "/data/seed/scam_keywords.json"
if not os.path.exists(SCAM_KEYWORDS_FILE):
    # Fallback to relative path if running locally outside Docker
    SCAM_KEYWORDS_FILE = os.path.join(os.path.dirname(__file__), "../../../data/seed/scam_keywords.json")

def load_scam_keywords() -> List[Dict]:
    try:
        with open(SCAM_KEYWORDS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("fee_indicators", [])
    except Exception:
        # Default safety keywords if file not found
        return [
            {"term": "registration fee", "weight": 25},
            {"term": "training kit", "weight": 25},
            {"term": "badge fee", "weight": 25},
            {"term": "frais de dossier", "weight": 25},
            {"term": "frais de formation", "weight": 25}
        ]

FEE_KEYWORDS = load_scam_keywords()
FREE_EMAIL_DOMAINS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "yandex.com"}

def compute_listing_risk_signals(listing: Listing, db: Session) -> Tuple[int, str, List[RiskSignal], str]:
    """
    Evaluates a single listing against the 6 deterministic risk rules.
    Returns:
    (final_score_0_to_100, risk_level, list_of_RiskSignal_objects, one_line_summary)
    """
    signals: List[RiskSignal] = []
    desc_lower = listing.description.lower()

    # Rule 1 & 2 & 5: Contact Reuse & Cross-Border Reuse
    for contact in listing.contacts:
        # Find all listings sharing this contact
        sibling_listings = (
            db.query(Listing)
            .join(Listing.contacts)
            .filter(Contact.id == contact.id)
            .all()
        )
        countries = list({l.country_code for l in sibling_listings})
        count = len(sibling_listings)

        # Cross-border reuse check
        if len(countries) > 1:
            countries_str = ", ".join(sorted(countries))
            signals.append(
                RiskSignal(
                    listing_id=listing.id,
                    rule_code="CROSS_BORDER_CONTACT",
                    severity="CRITICAL",
                    score_points=35,
                    explanation=f"This contact ({contact.normalized_value}) is actively advertising identical offers across multiple African countries ({countries_str})."
                )
            )

        # Multi-listing phone reuse
        if contact.contact_type == "PHONE" and count >= 2:
            signals.append(
                RiskSignal(
                    listing_id=listing.id,
                    rule_code="REUSED_PHONE_SYNDICATE",
                    severity="CRITICAL" if count >= 3 else "WARNING",
                    score_points=30 if count >= 3 else 20,
                    explanation=f"This phone number ({contact.normalized_value}) appears in {count} separate job listings under different titles."
                )
            )

        # Multi-listing email reuse
        if contact.contact_type == "EMAIL" and count >= 2:
            signals.append(
                RiskSignal(
                    listing_id=listing.id,
                    rule_code="REUSED_EMAIL_SYNDICATE",
                    severity="WARNING",
                    score_points=20,
                    explanation=f"This contact email is reused across {count} separate job ads."
                )
            )

        # Free webmail for purported corporate hiring
        if contact.contact_type == "EMAIL":
            domain = contact.normalized_value.split("@")[-1]
            if domain in FREE_EMAIL_DOMAINS and listing.poster_name and any(
                w in listing.poster_name.lower() for w in ["group", "ltd", "limited", "corp", "global", "firm", "company", "cabinet"]
            ):
                signals.append(
                    RiskSignal(
                        listing_id=listing.id,
                        rule_code="FREE_EMAIL_FOR_CORPORATE",
                        severity="INFO",
                        score_points=10,
                        explanation=f"Recruiter claims corporate hiring but relies on a free webmail address (@{domain})."
                    )
                )

    # Rule 4: Fee-solicitation keywords
    detected_terms = []
    for kw in FEE_KEYWORDS:
        if kw["term"].lower() in desc_lower:
            detected_terms.append(kw["term"])

    if detected_terms:
        terms_str = ", ".join(detected_terms[:2])
        signals.append(
            RiskSignal(
                listing_id=listing.id,
                rule_code="SUSPICIOUS_FEE_KEYWORD",
                severity="WARNING",
                score_points=25,
                explanation=f"Contains explicit requests for upfront payment ('{terms_str}'), a hallmark of employment scams."
            )
        )

    # Rule 3: Recycled text template from listing_links
    similarity_links = (
        db.query(ListingLink)
        .filter(
            ((ListingLink.source_listing_id == listing.id) | (ListingLink.target_listing_id == listing.id))
            & (ListingLink.link_type == "TEXT_SIMILARITY")
        )
        .all()
    )

    if similarity_links:
        best_sim = max([link.weight for link in similarity_links], default=0.0)
        sim_pct = int(best_sim * 100)
        signals.append(
            RiskSignal(
                listing_id=listing.id,
                rule_code="RECYCLED_TEXT_TEMPLATE",
                severity="WARNING",
                score_points=25,
                explanation=f"{sim_pct}% of this job description is identical to an ad posted under a different name or platform."
            )
        )

    # Deduplicate signals by rule_code to avoid repeated points
    unique_signals = {}
    for s in signals:
        if s.rule_code not in unique_signals or s.score_points > unique_signals[s.rule_code].score_points:
            unique_signals[s.rule_code] = s

    deduped_signals = list(unique_signals.values())

    # Total score calculation clamped to 100
    raw_score = sum(s.score_points for s in deduped_signals)
    final_score = min(100, raw_score)

    # Determine risk level
    if final_score >= 80:
        risk_level = "CRITICAL"
    elif final_score >= 60:
        risk_level = "HIGH"
    elif final_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # One-line explainable summary
    if not deduped_signals:
        summary = "LOW RISK: No scam syndicate indicators detected."
    else:
        # Sort by points descending
        sorted_sigs = sorted(deduped_signals, key=lambda s: s.score_points, reverse=True)
        top_sig = sorted_sigs[0].explanation
        if len(sorted_sigs) > 1:
            second_sig = sorted_sigs[1].explanation
            summary = f"{risk_level} RISK ({final_score}/100): {top_sig} Additionally, {second_sig}"
        else:
            summary = f"{risk_level} RISK ({final_score}/100): {top_sig}"

    return final_score, risk_level, deduped_signals, summary

def score_all_listings(db: Session) -> int:
    """Computes and updates risk scores and signals for all listings."""
    listings = db.query(Listing).all()
    # Delete existing signals
    db.query(RiskSignal).delete()
    db.flush()

    for listing in listings:
        score, level, signals, _ = compute_listing_risk_signals(listing, db)
        listing.risk_score = score
        listing.risk_level = level
        for sig in signals:
            db.add(sig)

    db.commit()
    return len(listings)
