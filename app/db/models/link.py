from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from sqlalchemy.sql import func
from app.db.base import Base


class Link(Base):
    __tablename__ = "links"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    source_url = Column(String(2048), nullable=False, index=True)  # URL where this link was found
    domain = Column(String(255), nullable=False, index=True)
    is_external = Column(Boolean, default=False, index=True)
    link_text = Column(Text, nullable=True)  # Anchor text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_links_domain_created', 'domain', 'created_at'),
        Index('idx_links_source_url', 'source_url'),
        Index('idx_links_url_hash', 'url'),
    )

