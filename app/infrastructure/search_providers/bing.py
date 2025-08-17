import httpx
from typing import List
from app.domain.entities import Backlink
from app.infrastructure.search_providers.base import BacklinkProvider
import structlog

logger = structlog.get_logger(__name__)


class BingBacklinkProvider(BacklinkProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
        self.headers = {
            "Ocp-Apim-Subscription-Key": api_key,
            "Accept": "application/json"
        }
    
    @property
    def provider_name(self) -> str:
        return "bing_search"
    
    async def is_available(self) -> bool:
        """Check if Bing API is available."""
        return bool(self.api_key)
    
    async def get_backlinks(self, url: str, limit: int = 10) -> List[Backlink]:
        """Get backlinks using Bing search API."""
        if not self.is_available():
            logger.warning("Bing provider not available")
            return []
        
        try:
            # Search for pages linking to the target URL
            query = f'link:"{url}"'
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "q": query,
                        "count": min(limit, 50),  # Bing allows up to 50
                        "responseFilter": "Webpages",
                        "mkt": "en-US"
                    },
                    headers=self.headers
                )
                response.raise_for_status()
                
                data = response.json()
                backlinks = []
                
                if "webPages" in data and "value" in data["webPages"]:
                    for page in data["webPages"]["value"]:
                        if len(backlinks) >= limit:
                            break
                        
                        backlink = Backlink(
                            backlink_url=page.get("url", ""),
                            backlink_title=page.get("name", ""),
                            backlink_domain=self._extract_domain(page.get("url", "")),
                            anchor_text=page.get("snippet", "")[:100] if page.get("snippet") else ""
                        )
                        backlinks.append(backlink)
                
                logger.info("Bing provider returned backlinks", 
                           count=len(backlinks), 
                           url=url)
                return backlinks
                
        except httpx.HTTPStatusError as e:
            logger.error("Bing API HTTP error", status_code=e.response.status_code, url=url)
        except httpx.RequestError as e:
            logger.error("Bing API request error", error=str(e), url=url)
        except Exception as e:
            logger.error("Bing API unexpected error", error=str(e), url=url)
        
        return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return ""


