"""
Apify Ingestion & Connector Service.

Executes an Apify Actor with APIFY_API_TOKEN, fetches scraped items from dataset,
extracts phone numbers and email addresses via regular expressions, converts ads
into the Ghost-Networks format, and triggers the detection & NetworkX graph analysis pipeline.
"""

import re
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from app.config import settings
from app.models.listing import Listing
from app.models.contact import Contact
from app.models.listing_contact import ListingContact
from app.models.network import NetworkCluster
from app.schemas.listing import ScrapedListingCreate, RawContactExtract
from app.services.cleaner import normalize_phone, normalize_email
from app.services.detector import detect_listing_links
from app.services.scorer import score_all_listings
from app.services.network_analyzer import analyze_and_save_networks

try:
    from apify_client import ApifyClient
except ImportError:
    ApifyClient = None


EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,4}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}(?:[\s.-]?\d{2,4})?")


def extract_contacts_regex(text: str) -> List[RawContactExtract]:
    """
    Extracts phone numbers and emails from unstructured text using regular expressions.
    """
    if not text:
        return []

    extracted: List[RawContactExtract] = []
    seen = set()

    # Extract emails
    for match in EMAIL_REGEX.finditer(text):
        email_val = match.group(0).strip().lower()
        key = ("EMAIL", email_val)
        if key not in seen:
            seen.add(key)
            extracted.append(RawContactExtract(raw_value=email_val, contact_type="EMAIL"))

    # Extract phones
    for match in PHONE_REGEX.finditer(text):
        raw_match = match.group(0).strip()
        digits = re.sub(r"\D", "", raw_match)
        # Valid African numbers have between 8 and 15 digits
        if 8 <= len(digits) <= 15:
            # Skip if it is purely a date or price (e.g. 2026-09-23 or 250000)
            if raw_match.count("-") == 2 and len(raw_match) == 10:
                continue
            key = ("PHONE", raw_match)
            if key not in seen:
                seen.add(key)
                extracted.append(RawContactExtract(raw_value=raw_match, contact_type="PHONE"))

    return extracted


def infer_country_code(raw_item: Dict[str, Any], extracted_contacts: List[RawContactExtract]) -> str:
    """
    Infers 3-letter ISO country code (CMR, NGA, KEN, GHA) from explicit fields,
    phone prefixes, or text mentions.
    """
    # 1. Check explicit country field
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

    # 2. Check extracted phone numbers
    for c in extracted_contacts:
        if c.contact_type == "PHONE":
            val = c.raw_value.replace(" ", "")
            if val.startswith("+237") or val.startswith("237"):
                return "CMR"
            if val.startswith("+234") or val.startswith("234"):
                return "NGA"
            if val.startswith("+254") or val.startswith("254"):
                return "KEN"
            if val.startswith("+233") or val.startswith("233"):
                return "GHA"

    # 3. Check text content
    combined_text = f"{raw_item.get('title', '')} {raw_item.get('description', '')}".lower()
    if any(term in combined_text for term in ("cameroun", "cameroon", "douala", "yaounde", "yaoundé", "bassa", "fcfa", "cfa")):
        return "CMR"
    if any(term in combined_text for term in ("nigeria", "lagos", "abuja", "ikeja", "ngn", "naira")):
        return "NGA"
    if any(term in combined_text for term in ("kenya", "nairobi", "mombasa", "kes", "ksh")):
        return "KEN"

    return "NGA"


def convert_apify_item_to_listing(item: Dict[str, Any]) -> ScrapedListingCreate:
    """
    Converts a single raw dictionary output from Apify scraper into Ghost-Networks format.
    """
    title = str(item.get("title") or item.get("job_title") or item.get("name") or "Job Opportunity").strip()
    description = str(item.get("description") or item.get("body") or item.get("text") or item.get("content") or "").strip()
    source_url = str(item.get("source_url") or item.get("url") or item.get("link") or "https://apify.com/dataset").strip()
    platform = str(item.get("platform") or item.get("source") or "apify_web").strip().lower()
    poster_name = item.get("poster_name") or item.get("company") or item.get("recruiter") or item.get("author")

    # Generate deterministic source_id if not present
    source_id = str(item.get("source_id") or item.get("id") or item.get("postId") or "").strip()
    if not source_id:
        hash_seed = f"{platform}_{title}_{source_url}_{description[:100]}"
        digest = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()[:12]
        source_id = f"apify_{platform}_{digest}"

    # Extract regex contacts from description & title
    contacts = extract_contacts_regex(f"{title}\n{description}")

    # Also include any pre-parsed contacts from item
    for explicit_email in item.get("emails", []):
        contacts.append(RawContactExtract(raw_value=str(explicit_email), contact_type="EMAIL"))
    for explicit_phone in item.get("phones", []):
        contacts.append(RawContactExtract(raw_value=str(explicit_phone), contact_type="PHONE"))
    if item.get("email"):
        contacts.append(RawContactExtract(raw_value=str(item["email"]), contact_type="EMAIL"))
    if item.get("phone"):
        contacts.append(RawContactExtract(raw_value=str(item["phone"]), contact_type="PHONE"))

    # Deduplicate contacts
    deduped_contacts: List[RawContactExtract] = []
    seen = set()
    for c in contacts:
        k = (c.contact_type, c.raw_value.strip().lower())
        if k not in seen:
            seen.add(k)
            deduped_contacts.append(c)

    # Country code
    country_code = infer_country_code(item, deduped_contacts)

    # Parse posted_at date
    posted_at = None
    raw_date = item.get("posted_at") or item.get("date") or item.get("publishedAt")
    if raw_date:
        if isinstance(raw_date, datetime):
            posted_at = raw_date
        elif isinstance(raw_date, str):
            try:
                posted_at = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            except Exception:
                posted_at = datetime.utcnow()

    return ScrapedListingCreate(
        source_id=source_id,
        title=title,
        description=description,
        platform=platform,
        country_code=country_code,
        poster_name=str(poster_name).strip() if poster_name else None,
        source_url=source_url,
        posted_at=posted_at or datetime.utcnow(),
        extracted_contacts=deduped_contacts
    )


def run_apify_actor(
    actor_id: str,
    run_input: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None,
    max_items: int = 50,
    timeout_secs: int = 120
) -> List[Dict[str, Any]]:
    """
    Executes an Apify Actor using the Apify Python Client and returns dataset items.
    """
    api_token = token or settings.APIFY_API_TOKEN
    if not api_token:
        raise ValueError(
            "APIFY_API_TOKEN is not configured. "
            "Please set APIFY_API_TOKEN in environment or pass 'token' in the request."
        )

    if ApifyClient is None:
        raise RuntimeError("apify-client library is not installed in the environment.")

    client = ApifyClient(token=api_token)
    actor_client = client.actor(actor_id)

    # Run the actor and wait for completion
    run_result = actor_client.call(
        run_input=run_input or {},
        timeout_secs=timeout_secs
    )

    if not run_result:
        raise RuntimeError(f"Failed to start or execute Apify actor '{actor_id}'.")

    dataset_id = run_result.get("defaultDatasetId")
    if not dataset_id:
        return []

    # Fetch items from dataset
    dataset_client = client.dataset(dataset_id)
    items_page = dataset_client.list_items(limit=max_items)
    return items_page.items


def ingest_and_analyze(
    db: Session,
    listings_data: List[ScrapedListingCreate]
) -> Dict[str, Any]:
    """
    Saves new listings and contacts to PostgreSQL, then triggers the link detection,
    risk scoring, and NetworkX network analysis pipeline.
    """
    inserted_ids: List[uuid.UUID] = []
    duplicate_count = 0
    contact_cache: Dict[str, Contact] = {}

    for item in listings_data:
        # Check duplicate
        existing = db.query(Listing).filter(Listing.source_id == item.source_id).first()
        if existing:
            duplicate_count += 1
            continue

        listing = Listing(
            id=uuid.uuid4(),
            source_id=item.source_id,
            title=item.title,
            description=item.description,
            platform=item.platform,
            country_code=item.country_code.upper(),
            poster_name=item.poster_name,
            source_url=item.source_url,
            posted_at=item.posted_at or datetime.utcnow(),
            risk_score=0,
            risk_level="LOW"
        )
        db.add(listing)
        db.flush()
        inserted_ids.append(listing.id)

        # Process extracted contacts
        contacts_to_process = list(item.extracted_contacts)
        # Extra regex extraction from description just in case
        for extra in extract_contacts_regex(item.description):
            if not any(c.contact_type == extra.contact_type and c.raw_value == extra.raw_value for c in contacts_to_process):
                contacts_to_process.append(extra)

        existing_contact_ids = {c.id for c in listing.contacts}
        seen_norms = set()

        for c_entry in contacts_to_process:
            raw_val = c_entry.raw_value
            c_type = c_entry.contact_type
            if not raw_val or not c_type:
                continue

            norm_val = None
            inferred_c = item.country_code.upper()

            if c_type == "EMAIL":
                norm_val = normalize_email(raw_val)
            elif c_type == "PHONE":
                res = normalize_phone(raw_val, item.country_code)
                if res:
                    norm_val, inferred_c = res

            if not norm_val or norm_val in seen_norms:
                continue
            seen_norms.add(norm_val)

            if norm_val in contact_cache:
                contact_obj = contact_cache[norm_val]
            else:
                contact_obj = db.query(Contact).filter(Contact.normalized_value == norm_val).first()
                if not contact_obj:
                    contact_obj = Contact(
                        id=uuid.uuid4(),
                        contact_type=c_type,
                        normalized_value=norm_val,
                        raw_sample=raw_val,
                        country_code=inferred_c,
                        listings_count=0
                    )
                    db.add(contact_obj)
                    db.flush()
                contact_cache[norm_val] = contact_obj

            has_link = (
                contact_obj.id in existing_contact_ids
                or contact_obj in listing.contacts
                or db.query(ListingContact).filter_by(listing_id=listing.id, contact_id=contact_obj.id).first() is not None
            )
            if not has_link:
                listing.contacts.append(contact_obj)
                existing_contact_ids.add(contact_obj.id)
                contact_obj.listings_count += 1

        db.commit()

    syndicates_detected = 0
    cross_border_syndicates = 0

    if inserted_ids:
        # Trigger links, scoring, and NetworkX network analysis
        detect_listing_links(db)
        score_all_listings(db)
        net_stats = analyze_and_save_networks(db)
        syndicates_detected = net_stats.get("clusters_created", 0)
        cross_border_syndicates = net_stats.get("cross_border_count", 0)
    else:
        # If no new listings inserted, query existing network counts
        syndicates_detected = db.query(NetworkCluster).count()
        cross_border_syndicates = db.query(NetworkCluster).filter(NetworkCluster.risk_score == 100).count()

    return {
        "inserted_count": len(inserted_ids),
        "duplicate_count": duplicate_count,
        "inserted_ids": inserted_ids,
        "syndicates_detected": syndicates_detected,
        "cross_border_syndicates": cross_border_syndicates
    }
