from typing import Dict, List
from pydantic import BaseModel

class TopScamContact(BaseModel):
    normalized_value: str
    contact_type: str
    listings_count: int
    countries: List[str]

class DashboardStatsResponse(BaseModel):
    total_listings: int
    total_contacts: int
    high_risk_listings: int
    total_networks: int
    cross_border_networks: int
    country_breakdown: Dict[str, int]
    platform_breakdown: Dict[str, int]
    top_scam_contacts: List[TopScamContact]
