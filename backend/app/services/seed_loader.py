import os
import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.listing import Listing
from app.models.contact import Contact
from app.models.listing_contact import ListingContact
from app.services.cleaner import normalize_phone, normalize_email, extract_contacts_from_text
from app.services.detector import detect_listing_links
from app.services.scorer import score_all_listings
from app.services.graph_service import cluster_and_save_networks

DEFAULT_SEED_FILE = "/data/seed/listings_sample.json"
if not os.path.exists(DEFAULT_SEED_FILE):
    DEFAULT_SEED_FILE = os.path.join(os.path.dirname(__file__), "../../../data/seed/listings_sample.json")

def load_seed_data(db: Session, seed_filepath: str = DEFAULT_SEED_FILE) -> int:
    """
    Parses seed JSON, ingests listings and contacts, runs link detection,
    risk scoring, and NetworkX clustering.
    """
    if not os.path.exists(seed_filepath):
        print(f"Seed file not found at {seed_filepath}. Skipping seed loading.")
        return 0

    with open(seed_filepath, "r", encoding="utf-8") as f:
        records = json.load(f)

    inserted_count = 0
    contact_cache = {}  # normalized_value -> Contact instance

    for r in records:
        # Check if already exists (support idempotency)
        existing = db.query(Listing).filter(Listing.source_id == r["source_id"]).first()
        if existing:
            listing = existing
            is_new = False
        else:
            posted_dt = None
            if r.get("posted_at"):
                try:
                    posted_dt = datetime.fromisoformat(r["posted_at"].replace("Z", "+00:00"))
                except Exception:
                    posted_dt = datetime.utcnow()

            listing = Listing(
                id=uuid.uuid4(),
                source_id=r["source_id"],
                title=r["title"],
                description=r["description"],
                platform=r["platform"],
                country_code=r["country_code"].upper(),
                poster_name=r.get("poster_name"),
                source_url=r["source_url"],
                posted_at=posted_dt,
                risk_score=0,
                risk_level="LOW"
            )
            db.add(listing)
            db.flush()
            is_new = True

        # Combine explicit contacts with extracted contacts from description
        all_raw_contacts = list(r.get("extracted_contacts", []))
        auto_extracted = extract_contacts_from_text(r.get("description", ""), r["country_code"])
        all_raw_contacts.extend(auto_extracted)

        # Track contacts already associated with this listing (in DB or session)
        existing_contact_ids = {c.id for c in listing.contacts}
        seen_norm_values_for_listing = set()

        # Normalize and deduplicate contacts for this listing
        for raw_c in all_raw_contacts:
            raw_val = raw_c.get("raw_value")
            c_type = raw_c.get("contact_type")
            if not raw_val or not c_type:
                continue

            norm_val = None
            inferred_country = r["country_code"].upper()

            if c_type == "EMAIL":
                norm_val = normalize_email(raw_val)
            elif c_type == "PHONE":
                norm_res = normalize_phone(raw_val, r["country_code"])
                if norm_res:
                    norm_val, inferred_country = norm_res

            if not norm_val:
                continue

            # Deduplicate per listing: skip if this normalized contact was already processed for this listing
            if norm_val in seen_norm_values_for_listing:
                continue
            seen_norm_values_for_listing.add(norm_val)

            # Check cache or DB for contact
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
                        country_code=inferred_country,
                        listings_count=0
                    )
                    db.add(contact_obj)
                    db.flush()
                contact_cache[norm_val] = contact_obj

            # Associate junction safely and idempotently
            has_association = (
                contact_obj.id in existing_contact_ids
                or contact_obj in listing.contacts
                or db.query(ListingContact).filter_by(listing_id=listing.id, contact_id=contact_obj.id).first() is not None
            )
            if not has_association:
                listing.contacts.append(contact_obj)
                existing_contact_ids.add(contact_obj.id)
                contact_obj.listings_count += 1

        if is_new:
            inserted_count += 1

    db.commit()

    if inserted_count > 0 or db.query(Listing).count() > 0:
        print(f"Ingested {inserted_count} listings. Running detection and risk scoring...")
        links_count = detect_listing_links(db)
        print(f"Detected {links_count} cross-listing links.")
        scored_count = score_all_listings(db)
        print(f"Computed explainable risk scores for {scored_count} listings.")
        networks_count = cluster_and_save_networks(db)
        print(f"Clustered {networks_count} scam syndicates via NetworkX.")

    return inserted_count
