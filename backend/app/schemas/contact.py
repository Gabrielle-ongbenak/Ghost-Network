import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ContactBase(BaseModel):
    contact_type: str
    normalized_value: str
    raw_sample: Optional[str] = None
    country_code: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: uuid.UUID
    listings_count: int
    first_seen_at: datetime
    last_seen_at: datetime

    model_config = ConfigDict(from_attributes=True)
