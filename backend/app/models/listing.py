import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    platform = Column(String(50), nullable=False, index=True)
    country_code = Column(String(3), nullable=False, index=True)
    poster_name = Column(String(150), nullable=True)
    source_url = Column(Text, nullable=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    scraped_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    risk_score = Column(Integer, nullable=False, default=0, index=True)
    risk_level = Column(String(20), nullable=False, default="LOW")  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    network_id = Column(UUID(as_uuid=True), ForeignKey("networks.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    contacts = relationship("Contact", secondary="listing_contacts", back_populates="listings")
    signals = relationship("RiskSignal", back_populates="listing", cascade="all, delete-orphan")
    network = relationship("NetworkCluster", back_populates="listings")
