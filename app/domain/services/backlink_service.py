from typing import List, Optional
from app.domain.entities import Backlink
from app.infrastructure.search_providers.base import BacklinkProvider
from app.infrastructure.search_providers.bing import BingBacklinkProvider
from app.infrastructure.search_providers.in_domain import InDomainBacklinkProvider
from app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)


class BacklinkService:
    def __init__(self):
        self.providers: List[BacklinkProvider] = []
        
        # Initialize providers based on configuration
        if settings.bing_api_key:
            self.providers.append(BingBacklinkProvider(settings.bing_api_key))
        
        # Always add in-domain provider as fallback
        self.providers.append(InDomainBacklinkProvider())
    
    async def get_backlinks(self, url: str, limit: int = 10) -> List[Backlink]:
        """Get backlinks for a given URL using multiple providers."""
        logger.info("Fetching backlinks", url=url, limit=limit)
        
        all_backlinks = []
        
        for provider in self.providers:
            try:
                if len(all_backlinks) >= limit:
                    break
                
                remaining_limit = limit - len(all_backlinks)
                backlinks = await provider.get_backlinks(url, remaining_limit)
                
                # Deduplicate backlinks
                for backlink in backlinks:
                    if not self._is_duplicate_backlink(backlink, all_backlinks):
                        all_backlinks.append(backlink)
                        if len(all_backlinks) >= limit:
                            break
                
                logger.info("Provider returned backlinks", 
                           provider=provider.__class__.__name__,
                           count=len(backlinks),
                           url=url)
                
            except Exception as e:
                logger.error("Error with backlink provider", 
                           provider=provider.__class__.__name__,
                           url=url,
                           error=str(e))
                continue
        
        # Limit to requested number
        result = all_backlinks[:limit]
        logger.info("Total backlinks found", 
                   url=url, 
                   total=len(result), 
                   requested=limit)
        
        return result
    
    def _is_duplicate_backlink(self, new_backlink: Backlink, existing_backlinks: List[Backlink]) -> bool:
        """Check if a backlink already exists in the list."""
        for existing in existing_backlinks:
            if existing.backlink_url == new_backlink.backlink_url:
                return True
        return False
    
    async def get_backlink_summary(self, url: str) -> dict:
        """Get a summary of backlink information without full processing."""
        try:
            # Try to get just a few backlinks for summary
            sample_backlinks = await self.get_backlinks(url, limit=5)
            
            return {
                "url": url,
                "sample_backlinks_count": len(sample_backlinks),
                "providers_available": len(self.providers),
                "has_bing_provider": any(isinstance(p, BingBacklinkProvider) for p in self.providers)
            }
        except Exception as e:
            logger.error("Error getting backlink summary", url=url, error=str(e))
            return {"error": str(e)}


