from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class LinkType(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"


@dataclass
class Link:
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    domain: Optional[str] = None
    link_type: LinkType = LinkType.EXTERNAL
    link_text: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.domain and self.url:
            from urllib.parse import urlparse
            parsed = urlparse(self.url)
            self.domain = parsed.netloc


@dataclass
class Backlink:
    backlink_url: str
    backlink_title: Optional[str] = None
    backlink_domain: Optional[str] = None
    anchor_text: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class IngestionJob:
    source_url: str
    status: str = "pending"
    total_links_found: int = 0
    total_backlinks_found: int = 0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class IngestionResult:
    job: IngestionJob
    links: List[Link]
    backlinks: List[Backlink]
    total_links: int
    total_backlinks: int

