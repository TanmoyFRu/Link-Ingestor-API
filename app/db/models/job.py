from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Index
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    source_url = Column(String(2048), nullable=False, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, index=True)
    total_links_found = Column(Integer, default=0)
    total_backlinks_found = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_jobs_status', 'status'),
        Index('idx_jobs_created', 'created_at'),
        Index('idx_jobs_source_url', 'source_url'),
    )

