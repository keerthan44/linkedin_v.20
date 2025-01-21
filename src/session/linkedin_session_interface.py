from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from ..browser.scraper_interface import ScraperInterface

class LinkedInSessionInterface(ABC):
    """
    Interface for LinkedIn session management.
    Handles browser lifecycle, authentication, and session state.
    """

    @abstractmethod
    async def initialize(self, **kwargs) -> None:
        """Initialize browser and session."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close browser and cleanup resources."""
        pass

    @abstractmethod
    async def login(self, username: str, password: str) -> bool:
        """
        Login to LinkedIn.
        
        Args:
            username: LinkedIn username/email
            password: LinkedIn password
            
        Returns:
            bool: True if login successful
        """
        pass

    @abstractmethod
    async def validate_session(self) -> bool:
        """
        Check if current session is valid.
        
        Returns:
            bool: True if session is valid and logged in
        """
        pass

    @abstractmethod
    def get_browser(self) -> Any:
        """Get the current browser instance."""
        pass

    @abstractmethod
    def get_scraper(self) -> ScraperInterface:
        """Get the scraper instance."""
        pass 