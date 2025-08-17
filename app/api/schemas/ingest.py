from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime


class IngestRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL of the page to ingest")
    include_backlinks: bool = Field(default=True, description="Whether to fetch backlinks")
    max_backlinks_per_link: int = Field(default=10, ge=1, le=50, description="Maximum backlinks per link")


class LinkResponse(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    source_url: str
    domain: str
    is_external: bool
    link_text: Optional[str] = None
    created_at: Optional[datetime] = None


class BacklinkResponse(BaseModel):
    backlink_url: str
    backlink_title: Optional[str] = None
    backlink_domain: str
    anchor_text: Optional[str] = None
    created_at: Optional[datetime] = None


class IngestResponse(BaseModel):
    job_id: str
    source_url: str
    status: str
    total_links_found: int
    total_backlinks_found: int
    links: List[LinkResponse]
    backlinks: List[BacklinkResponse]
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class IngestSummaryResponse(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    total_links_found: int
    external_links: int
    internal_links: int
    content_type: Optional[str] = None
    status_code: Optional[int] = None


