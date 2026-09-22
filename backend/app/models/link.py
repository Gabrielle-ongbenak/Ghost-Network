import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class ListingLink(Base):
    __tablename__ = "listing_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True)
    target_listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True)
    link_type = Column(String(40), nullable=False)  # 'REUSED_PHONE', 'REUSED_EMAIL', 'TEXT_SIMILARITY', 'SAME_POSTER'
    weight = Column(Float, nullable=False, default=1.0)
    metadata_info = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    source_listing = relationship("Listing", foreign_keys=[source_listing_id])
    target_listing = relationship("Listing", foreign_keys=[target_listing_id])

    __table_args__ = (
        Index("idx_links_source_target", "source_listing_id", "target_listing_id"),
    )
