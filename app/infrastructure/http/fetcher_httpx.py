import httpx
from typing import Optional, Dict, Any
from app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)


class HTTPFetcher:
    def __init__(self):
        self.timeout = httpx.Timeout(settings.http_timeout)
        self.headers = {
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
    
    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a web page and return its content and metadata."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                response.raise_for_status()
                
                return {
                    "url": url,
                    "status_code": response.status_code,
                    "content": response.text,
                    "content_type": response.headers.get("content-type", ""),
                    "final_url": str(response.url),
                    "headers": dict(response.headers),
                }
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error fetching page", url=url, status_code=e.response.status_code)
            return None
        except httpx.RequestError as e:
            logger.error("Request error fetching page", url=url, error=str(e))
            return None
        except Exception as e:
            logger.error("Unexpected error fetching page", url=url, error=str(e))
            return None
    
    async def check_robots_txt(self, domain: str) -> Optional[str]:
        """Check robots.txt for a domain."""
        try:
            robots_url = f"https://{domain}/robots.txt"
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(robots_url, headers=self.headers)
                if response.status_code == 200:
                    return response.text
                return None
        except Exception as e:
            logger.error("Error checking robots.txt", domain=domain, error=str(e))
            return None

