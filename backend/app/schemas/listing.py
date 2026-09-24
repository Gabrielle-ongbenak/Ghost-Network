import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.contact import ContactResponse
from app.schemas.signal import RiskSignalResponse

class RawContactExtract(BaseModel):
    raw_value: str
    contact_type: str = Field(..., description="'PHONE' or 'EMAIL'")

class ScrapedListingCreate(BaseModel):
    source_id: str
    title: str
    description: str
    platform: str
    country_code: str = Field(..., min_length=2, max_length=3)
    poster_name: Optional[str] = None
    source_url: str
    posted_at: Optional[datetime] = None
    extracted_contacts: List[RawContactExtract] = Field(default_factory=list)

class BulkIngestRequest(BaseModel):
    listings: List[ScrapedListingCreate]

class BulkIngestResponse(BaseModel):
    status: str
    received_count: int
    inserted_count: int
    duplicate_count: int
    inserted_ids: List[uuid.UUID]

class ApifyIngestRequest(BaseModel):
    actor_id: str = Field(default="ghost-networks-scraper", description="Apify Actor ID or name")
    run_input: Optional[dict] = Field(default=None, description="Input parameters for the Apify Actor")
    token: Optional[str] = Field(default=None, description="Apify API Token (falls back to settings.APIFY_API_TOKEN)")
    max_items: Optional[int] = Field(default=50, description="Max items to retrieve from dataset")
    sample_items: Optional[List[dict]] = Field(default=None, description="Direct ad objects for offline simulation or testing")

class ApifyIngestResponse(BaseModel):
    status: str
    actor_id: str
    items_scraped: int
    inserted_count: int
    duplicate_count: int
    inserted_ids: List[uuid.UUID]
    syndicates_detected: int
    cross_border_syndicates: int

class ListingSummary(BaseModel):
    id: uuid.UUID
    source_id: str
    title: str
    platform: str
    country_code: str
    poster_name: Optional[str] = None
    source_url: str
    posted_at: Optional[datetime] = None
    risk_score: int
    risk_level: str
    network_id: Optional[uuid.UUID] = None
    detected_signals_count: int = 0
    contacts_summary: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class LinkedListingRef(BaseModel):
    id: uuid.UUID
    title: str
    country_code: str
    platform: str
    link_type: str
    weight: float
    evidence: Optional[str] = None

class ListingDetail(BaseModel):
    id: uuid.UUID
    source_id: str
    title: str
    description: str
    platform: str
    country_code: str
    poster_name: Optional[str] = None
    source_url: str
    posted_at: Optional[datetime] = None
    scraped_at: datetime
    risk_score: int
    risk_level: str
    network_id: Optional[uuid.UUID] = None
    one_line_summary: str
    signals: List[RiskSignalResponse] = Field(default_factory=list)
    contacts: List[ContactResponse] = Field(default_factory=list)
    linked_listings: List[LinkedListingRef] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class ListingPaginationResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[ListingSummary]
