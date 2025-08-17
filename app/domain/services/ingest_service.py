from typing import List, Optional
from app.domain.entities import Link, Backlink, IngestionJob, IngestionResult
from app.infrastructure.http.fetcher_httpx import HTTPFetcher
from app.infrastructure.parsers.html import HTMLParser
from app.domain.services.backlink_service import BacklinkService
from app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)


class IngestService:
    def __init__(self):
        self.http_fetcher = HTTPFetcher()
        self.html_parser = HTMLParser()
        self.backlink_service = BacklinkService()
    
    async def ingest_page(self, url: str) -> IngestionResult:
        """Main method to ingest a page and extract all links with backlinks."""
        logger.info("Starting page ingestion", url=url)
        
        # Create job
        job = IngestionJob(source_url=url)
        
        try:
            # Fetch the page
            page_data = await self.http_fetcher.fetch_page(url)
            if not page_data:
                job.status = "failed"
                job.error_message = "Failed to fetch page"
                return IngestionResult(
                    job=job,
                    links=[],
                    backlinks=[],
                    total_links=0,
                    total_backlinks=0
                )
            
            # Parse links from HTML
            raw_links = self.html_parser.parse_links(page_data["content"], url)
            logger.info("Extracted raw links", count=len(raw_links), url=url)
            
            # Convert to domain entities
            links = []
            for raw_link in raw_links:
                link = Link(
                    url=raw_link["url"],
                    title=raw_link.get("title", ""),
                    link_text=raw_link.get("link_text", ""),
                    source_url=url,
                    domain=raw_link["domain"],
                    link_type="external" if raw_link["is_external"] else "internal"
                )
                links.append(link)
            
            # Remove duplicates
            unique_links = self._deduplicate_links(links)
            job.total_links_found = len(unique_links)
            
            # Fetch backlinks for each link (limited to max_backlinks_per_link)
            all_backlinks = []
            for link in unique_links:
                backlinks = await self.backlink_service.get_backlinks(
                    link.url, 
                    limit=settings.max_backlinks_per_link
                )
                all_backlinks.extend(backlinks)
            
            job.total_backlinks_found = len(all_backlinks)
            job.status = "completed"
            
            logger.info("Page ingestion completed", 
                       url=url, 
                       links_found=len(unique_links),
                       backlinks_found=len(all_backlinks))
            
            return IngestionResult(
                job=job,
                links=unique_links,
                backlinks=all_backlinks,
                total_links=len(unique_links),
                total_backlinks=len(all_backlinks)
            )
            
        except Exception as e:
            logger.error("Error during page ingestion", url=url, error=str(e))
            job.status = "failed"
            job.error_message = str(e)
            
            return IngestionResult(
                job=job,
                links=[],
                backlinks=[],
                total_links=0,
                total_backlinks=0
            )
    
    def _deduplicate_links(self, links: List[Link]) -> List[Link]:
        """Remove duplicate links based on URL."""
        seen_urls = set()
        unique_links = []
        
        for link in links:
            if link.url not in seen_urls:
                seen_urls.add(link.url)
                unique_links.append(link)
        
        return unique_links
    
    async def get_ingestion_summary(self, url: str) -> dict:
        """Get a summary of ingestion results without full processing."""
        try:
            page_data = await self.http_fetcher.fetch_page(url)
            if not page_data:
                return {"error": "Failed to fetch page"}
            
            raw_links = self.html_parser.parse_links(page_data["content"], url)
            metadata = self.html_parser.extract_page_metadata(page_data["content"])
            
            return {
                "url": url,
                "title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
                "total_links_found": len(raw_links),
                "external_links": len([l for l in raw_links if l["is_external"]]),
                "internal_links": len([l for l in raw_links if not l["is_external"]]),
                "content_type": page_data["content_type"],
                "status_code": page_data["status_code"]
            }
        except Exception as e:
            logger.error("Error getting ingestion summary", url=url, error=str(e))
            return {"error": str(e)}


