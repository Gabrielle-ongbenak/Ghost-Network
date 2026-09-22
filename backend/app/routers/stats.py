from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.listing import Listing
from app.models.contact import Contact
from app.models.network import NetworkCluster
from app.schemas.stats import DashboardStatsResponse, TopScamContact

router = APIRouter(prefix="/stats", tags=["Dashboard Statistics"])

@router.get("/overview", response_model=DashboardStatsResponse)
def get_dashboard_overview(db: Session = Depends(get_db)):
    """Computes aggregated KPIs and breakdowns for the Streamlit dashboard."""
    total_listings = db.query(Listing).count()
    total_contacts = db.query(Contact).count()
    high_risk_listings = db.query(Listing).filter(Listing.risk_score >= 60).count()
    total_networks = db.query(NetworkCluster).count()

    # Cross-border networks
    all_networks = db.query(NetworkCluster).all()
    cross_border_count = sum(1 for net in all_networks if len(net.countries_involved) > 1)

    # Country & platform breakdowns
    listings = db.query(Listing.country_code, Listing.platform).all()
    country_counts = Counter(l[0] for l in listings)
    platform_counts = Counter(l[1] for l in listings)

    # Top scam contacts (contacts with highest listing counts)
    top_contacts_raw = db.query(Contact).order_by(Contact.listings_count.desc()).limit(5).all()
    top_contacts = []
    for c in top_contacts_raw:
        countries = list({l.country_code for l in c.listings})
        top_contacts.append(
            TopScamContact(
                normalized_value=c.normalized_value,
                contact_type=c.contact_type,
                listings_count=c.listings_count,
                countries=sorted(countries)
            )
        )

    return DashboardStatsResponse(
        total_listings=total_listings,
        total_contacts=total_contacts,
        high_risk_listings=high_risk_listings,
        total_networks=total_networks,
        cross_border_networks=cross_border_count,
        country_breakdown=dict(country_counts),
        platform_breakdown=dict(platform_counts),
        top_scam_contacts=top_contacts
    )
