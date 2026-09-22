import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.listing import Listing
from app.models.link import ListingLink
from app.schemas.listing import (
    ListingPaginationResponse,
    ListingSummary,
    ListingDetail,
    LinkedListingRef
)
from app.schemas.signal import RiskSignalResponse
from app.schemas.contact import ContactResponse
from app.services.scorer import compute_listing_risk_signals

router = APIRouter(prefix="/listings", tags=["Listings"])

@router.get("", response_model=ListingPaginationResponse)
def list_listings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    country: Optional[str] = Query(None, description="Country alpha code (CMR, NGA, KEN)"),
    platform: Optional[str] = Query(None, description="Platform (jiji, jobberman, etc.)"),
    min_risk: int = Query(0, ge=0, le=100),
    network_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Listing)

    if country:
        query = query.filter(Listing.country_code == country.upper())
    if platform:
        query = query.filter(Listing.platform.ilike(f"%{platform}%"))
    if min_risk > 0:
        query = query.filter(Listing.risk_score >= min_risk)
    if network_id:
        query = query.filter(Listing.network_id == network_id)

    total = query.count()
    items_raw = query.order_by(Listing.risk_score.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for l in items_raw:
        contacts_summary = [c.normalized_value for c in l.contacts]
        items.append(
            ListingSummary(
                id=l.id,
                source_id=l.source_id,
                title=l.title,
                platform=l.platform,
                country_code=l.country_code,
                poster_name=l.poster_name,
                source_url=l.source_url,
                posted_at=l.posted_at,
                risk_score=l.risk_score,
                risk_level=l.risk_level,
                network_id=l.network_id,
                detected_signals_count=len(l.signals),
                contacts_summary=contacts_summary
            )
        )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return ListingPaginationResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items
    )

@router.get("/{listing_id}", response_model=ListingDetail)
def get_listing_detail(listing_id: uuid.UUID, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    # Compute current explainable summary
    _, _, _, one_line_summary = compute_listing_risk_signals(listing, db)

    # Fetch connected listings via listing_links
    links = db.query(ListingLink).filter(
        (ListingLink.source_listing_id == listing.id) | (ListingLink.target_listing_id == listing.id)
    ).all()

    linked_listings = []
    for link in links:
        other_id = link.target_listing_id if link.source_listing_id == listing.id else link.source_listing_id
        other = db.query(Listing).filter(Listing.id == other_id).first()
        if other:
            evidence_str = ""
            if link.metadata_info:
                if "matched_value" in link.metadata_info:
                    evidence_str = f"Matches contact {link.metadata_info['matched_value']}"
                elif "similarity_score" in link.metadata_info:
                    evidence_str = f"{link.metadata_info['similarity_score']}% template similarity"

            linked_listings.append(
                LinkedListingRef(
                    id=other.id,
                    title=other.title,
                    country_code=other.country_code,
                    platform=other.platform,
                    link_type=link.link_type,
                    weight=link.weight,
                    evidence=evidence_str
                )
            )

    signals_resp = [
        RiskSignalResponse(
            id=s.id,
            rule_code=s.rule_code,
            severity=s.severity,
            score_points=s.score_points,
            explanation=s.explanation,
            created_at=s.created_at
        ) for s in listing.signals
    ]

    contacts_resp = [
        ContactResponse(
            id=c.id,
            contact_type=c.contact_type,
            normalized_value=c.normalized_value,
            raw_sample=c.raw_sample,
            country_code=c.country_code,
            listings_count=c.listings_count,
            first_seen_at=c.first_seen_at,
            last_seen_at=c.last_seen_at
        ) for c in listing.contacts
    ]

    return ListingDetail(
        id=listing.id,
        source_id=listing.source_id,
        title=listing.title,
        description=listing.description,
        platform=listing.platform,
        country_code=listing.country_code,
        poster_name=listing.poster_name,
        source_url=listing.source_url,
        posted_at=listing.posted_at,
        scraped_at=listing.scraped_at,
        risk_score=listing.risk_score,
        risk_level=listing.risk_level,
        network_id=listing.network_id,
        one_line_summary=one_line_summary,
        signals=signals_resp,
        contacts=contacts_resp,
        linked_listings=linked_listings
    )
