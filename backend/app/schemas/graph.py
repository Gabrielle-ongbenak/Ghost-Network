import uuid
from typing import List, Optional
from pydantic import BaseModel, Field

class GraphNode(BaseModel):
    id: str
    label: str
    group: str  # "listing" or "contact"
    country: Optional[str] = None
    risk_score: int
    color: str
    size: int
    title: str  # Tooltip text

class GraphEdge(BaseModel):
    id: Optional[str] = None
    source: str = Field(..., alias="from")
    target: str = Field(..., alias="to")
    label: Optional[str] = None
    link_type: str
    weight: float = 1.0
    color: str = "#888888"
    width: int = 1
    title: Optional[str] = None

    class Config:
        populate_by_name = True

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class NetworkSummary(BaseModel):
    id: uuid.UUID
    label: str
    risk_score: int
    listings_count: int
    contacts_count: int
    countries_involved: List[str]
    platforms_involved: List[str]
