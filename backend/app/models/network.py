import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class NetworkCluster(Base):
    __tablename__ = "networks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label = Column(String(150), nullable=False)
    risk_score = Column(Integer, nullable=False, default=0)
    listings_count = Column(Integer, nullable=False, default=0)
    contacts_count = Column(Integer, nullable=False, default=0)
    countries_involved = Column(JSONB, nullable=False, default=list)
    platforms_involved = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    listings = relationship("Listing", back_populates="network")
