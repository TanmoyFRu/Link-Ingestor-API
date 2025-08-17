from typing import List, Set
from urllib.parse import urljoin, urlparse
from app.domain.entities import Backlink
from app.infrastructure.search_providers.base import BacklinkProvider
from app.infrastructure.http.fetcher_httpx import HTTPFetcher
from app.infrastructure.parsers.html import HTMLParser
import structlog
from bs4 import BeautifulSoup

logger = structlog.get_logger(__name__)


class InDomainBacklinkProvider(BacklinkProvider):
    def __init__(self):
        self.http_fetcher = HTTPFetcher()
        self.html_parser = HTMLParser()
        self.visited_urls: Set[str] = set()
        self.max_depth = 2  # Limit crawling depth
    
    @property
    def provider_name(self) -> str:
        return "in_domain_search"
    
    async def is_available(self) -> bool:
        """In-domain provider is always available."""
        return True
    
    async def get_backlinks(self, url: str, limit: int = 10) -> List[Backlink]:
        """Find backlinks by crawling the same domain."""
        try:
            domain = urlparse(url).netloc
            if not domain:
                return []
            
            logger.info("Starting in-domain backlink search", url=url, domain=domain)
            
            # Start crawling from the domain root
            root_url = f"https://{domain}"
            backlinks = await self._crawl_domain_for_backlinks(
                root_url, url, domain, limit, depth=0
            )
            
            logger.info("In-domain provider found backlinks", 
                       count=len(backlinks), 
                       url=url)
            return backlinks[:limit]
            
        except Exception as e:
            logger.error("Error in in-domain backlink search", url=url, error=str(e))
            return []
    
    async def _crawl_domain_for_backlinks(
        self, 
        crawl_url: str, 
        target_url: str, 
        domain: str, 
        limit: int, 
        depth: int
    ) -> List[Backlink]:
        """Recursively crawl domain to find pages linking to target URL."""
        if depth > self.max_depth or len(self.visited_urls) > 100:
            return []
        
        if crawl_url in self.visited_urls:
            return []
        
        self.visited_urls.add(crawl_url)
        backlinks = []
        
        try:
            # Fetch the page
            page_data = await self.http_fetcher.fetch_page(crawl_url)
            if not page_data:
                return backlinks
            
            # Check if this page links to our target
            if target_url in page_data["content"]:
                # Extract page title
                soup = BeautifulSoup(page_data["content"], "lxml")
                title = soup.find("title")
                title_text = title.get_text(strip=True) if title else ""
                
                backlink = Backlink(
                    backlink_url=crawl_url,
                    backlink_title=title_text,
                    backlink_domain=domain,
                    anchor_text=f"Found link to {target_url}"
                )
                backlinks.append(backlink)
                
                if len(backlinks) >= limit:
                    return backlinks
            
            # If we haven't found enough backlinks, crawl linked pages
            if len(backlinks) < limit and depth < self.max_depth:
                raw_links = self.html_parser.parse_links(page_data["content"], crawl_url)
                
                # Filter to same-domain links
                same_domain_links = [
                    link for link in raw_links 
                    if link["domain"] == domain and not link["is_external"]
                ]
                
                # Recursively crawl these links
                for link in same_domain_links[:5]:  # Limit recursion
                    if len(backlinks) >= limit:
                        break
                    
                    sub_backlinks = await self._crawl_domain_for_backlinks(
                        link["url"], target_url, domain, limit - len(backlinks), depth + 1
                    )
                    backlinks.extend(sub_backlinks)
            
        except Exception as e:
            logger.error("Error crawling page", url=crawl_url, error=str(e))
        
        return backlinks


