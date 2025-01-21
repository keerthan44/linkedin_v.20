from abc import ABC, abstractmethod
import logging
from typing import Optional, Dict, Any, List

from ..session.linkedin_session_interface import LinkedInSessionInterface

logger = logging.getLogger(__name__)

class BaseLinkedInScraper(ABC):
    """
    Abstract base class for LinkedIn scrapers.
    """

    def __init__(self, session: LinkedInSessionInterface):
        """
        Initialize with a session manager.
        
        Args:
            session: LinkedIn session manager instance
        """
        self._session = session
        self._scraper = session.get_scraper()

    @abstractmethod
    async def extract_data(self, html: str, data_type: str) -> Dict[str, Any]:
        """Extract structured data from LinkedIn HTML."""
        pass

    @abstractmethod
    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate extracted data."""
        pass

    async def ensure_logged_in(self) -> bool:
        """
        Ensure we're logged into LinkedIn before scraping.
        
        Returns:
            bool: True if logged in, False otherwise
        """
        return self._session.is_logged_in() 