import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.graph import GraphResponse
from app.services.graph_service import build_graph_response

router = APIRouter(prefix="/graph", tags=["Network Graph"])

@router.get("", response_model=GraphResponse)
def get_network_graph(
    network_id: Optional[uuid.UUID] = Query(None, description="Filter nodes to a specific syndicate cluster"),
    min_risk: int = Query(0, ge=0, le=100, description="Minimum risk score filter"),
    max_nodes: int = Query(150, ge=10, le=500, description="Max nodes to return to prevent visual lag"),
    db: Session = Depends(get_db)
):
    """
    Returns graph nodes and edges optimized for interactive Pyvis visualization.
    Nodes represent job ads and suspicious contacts. Edges represent shared contacts and duplicate templates.
    """
    return build_graph_response(db, network_id=network_id, min_risk=min_risk, max_nodes=max_nodes)
