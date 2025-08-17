from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Backlink(Base):
    __tablename__ = "backlinks"
    
    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(Integer, ForeignKey("links.id"), nullable=False, index=True)
    backlink_url = Column(String(2048), nullable=False, index=True)
    backlink_title = Column(String(500), nullable=True)
    backlink_domain = Column(String(255), nullable=False, index=True)
    anchor_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    link = relationship("Link", back_populates="backlinks")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_backlinks_link_id', 'link_id'),
        Index('idx_backlinks_domain', 'backlink_domain'),
        Index('idx_backlinks_created', 'created_at'),
    )

