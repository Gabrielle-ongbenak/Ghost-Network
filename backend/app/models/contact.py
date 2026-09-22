import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_type = Column(String(10), nullable=False)  # 'PHONE' or 'EMAIL'
    normalized_value = Column(String(128), unique=True, nullable=False, index=True)
    raw_sample = Column(String(128), nullable=True)
    country_code = Column(String(3), nullable=True, index=True)
    listings_count = Column(Integer, nullable=False, default=1)
    first_seen_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_seen_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    listings = relationship("Listing", secondary="listing_contacts", back_populates="contacts")
