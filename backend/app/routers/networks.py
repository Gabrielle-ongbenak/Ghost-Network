import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.network import NetworkCluster
from app.schemas.graph import NetworkSummary

router = APIRouter(prefix="/networks", tags=["Scam Syndicates"])

@router.get("", response_model=List[NetworkSummary])
def list_networks(db: Session = Depends(get_db)):
    """Lists all detected scam syndicates sorted by risk score descending."""
    clusters = db.query(NetworkCluster).order_by(NetworkCluster.risk_score.desc()).all()
    return [
        NetworkSummary(
            id=c.id,
            label=c.label,
            risk_score=c.risk_score,
            listings_count=c.listings_count,
            contacts_count=c.contacts_count,
            countries_involved=c.countries_involved,
            platforms_involved=c.platforms_involved
        ) for c in clusters
    ]

@router.get("/{network_id}", response_model=NetworkSummary)
def get_network(network_id: uuid.UUID, db: Session = Depends(get_db)):
    """Returns single scam syndicate details."""
    cluster = db.query(NetworkCluster).filter(NetworkCluster.id == network_id).first()
    if not cluster:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Syndicate cluster not found")
    return NetworkSummary(
        id=cluster.id,
        label=cluster.label,
        risk_score=cluster.risk_score,
        listings_count=cluster.listings_count,
        contacts_count=cluster.contacts_count,
        countries_involved=cluster.countries_involved,
        platforms_involved=cluster.platforms_involved
    )
