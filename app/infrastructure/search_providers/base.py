from abc import ABC, abstractmethod
from typing import List
from app.domain.entities import Backlink


class BacklinkProvider(ABC):
    """Base interface for backlink providers."""
    
    @abstractmethod
    async def get_backlinks(self, url: str, limit: int = 10) -> List[Backlink]:
        """Retrieve backlinks for a given URL."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider is available and working."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider."""
        pass



