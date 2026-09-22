import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.listing import Listing
from app.models.contact import Contact
from app.models.listing_contact import ListingContact
from app.schemas.listing import BulkIngestRequest, BulkIngestResponse
from app.services.cleaner import normalize_phone, normalize_email, extract_contacts_from_text
from app.services.detector import detect_listing_links
from app.services.scorer import score_all_listings
from app.services.graph_service import cluster_and_save_networks

router = APIRouter(prefix="/ingest", tags=["Ingestion & Pipeline"])

@router.post("/bulk", response_model=BulkIngestResponse, status_code=status.HTTP_201_CREATED)
def bulk_ingest_listings(payload: BulkIngestRequest, db: Session = Depends(get_db)):
    """
    Ingests a batch of scraped listings, extracts and normalizes contacts,
    and runs the detection & risk scoring pipeline.
    """
    received_count = len(payload.listings)
    inserted_ids = []
    duplicate_count = 0
    contact_cache = {}

    for item in payload.listings:
        # Check duplicate by source_id
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

        # Merge extracted contacts
        all_contacts = [{"raw_value": c.raw_value, "contact_type": c.contact_type} for c in item.extracted_contacts]
        auto_extracted = extract_contacts_from_text(item.description, item.country_code)
        all_contacts.extend(auto_extracted)

        # Track contacts already associated with this listing
        existing_contact_ids = {c.id for c in listing.contacts}
        seen_norm_values_for_listing = set()

        for c_entry in all_contacts:
            raw_val = c_entry.get("raw_value")
            c_type = c_entry.get("contact_type")
            if not raw_val or not c_type:
                continue

            norm_val = None
            inferred_country = item.country_code.upper()

            if c_type == "EMAIL":
                norm_val = normalize_email(raw_val)
            elif c_type == "PHONE":
                res = normalize_phone(raw_val, item.country_code)
                if res:
                    norm_val, inferred_country = res

            if not norm_val:
                continue

            # Deduplicate per listing
            if norm_val in seen_norm_values_for_listing:
                continue
            seen_norm_values_for_listing.add(norm_val)

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

        db.commit()

    if inserted_ids:
        # Run detection and scoring pipeline
        detect_listing_links(db)
        score_all_listings(db)
        cluster_and_save_networks(db)

    return BulkIngestResponse(
        status="success",
        received_count=received_count,
        inserted_count=len(inserted_ids),
        duplicate_count=duplicate_count,
        inserted_ids=inserted_ids
    )

@router.post("/run-detection")
def trigger_detection_pipeline(db: Session = Depends(get_db)):
    """
    Manually triggers the detection, link creation, risk scoring,
    and NetworkX community clustering pipeline across all listings.
    """
    links_count = detect_listing_links(db)
    scored_count = score_all_listings(db)
    clusters_count = cluster_and_save_networks(db)

    return {
        "status": "completed",
        "links_created": links_count,
        "listings_scored": scored_count,
        "syndicates_identified": clusters_count
    }
