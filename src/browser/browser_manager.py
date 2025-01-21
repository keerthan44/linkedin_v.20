from abc import ABC, abstractmethod
from typing import Any, Optional

class BrowserManager(ABC):
    """
    Abstract base class for browser management operations.
    Handles browser lifecycle and provides interface for browser interactions.
    """
    
    def __init__(self):
        self._browser = None
        self._context = None
        self._is_initialized = False

    @abstractmethod
    async def start_browser(self, **kwargs) -> None:
        """
        Initialize and start the browser with given configuration.
        
        Args:
            **kwargs: Browser-specific configuration options
        """
        pass

    @abstractmethod
    async def close_browser(self) -> None:
        """Close the browser and cleanup resources."""
        pass

    @abstractmethod
    def is_browser_open(self) -> bool:
        """
        Check if browser is currently open and ready.
        
        Returns:
            bool: True if browser is open and ready, False otherwise
        """
        pass

    @abstractmethod
    def get_browser_instance(self) -> Any:
        """
        Get the current browser instance.
        
        Returns:
            Any: The browser instance object
        
        Raises:
            BrowserNotInitializedError: If browser hasn't been started
        """
        pass

    async def restart_browser(self, **kwargs) -> None:
        """
        Restart the browser with given configuration.
        
        Args:
            **kwargs: Browser-specific configuration options
        """
        await self.close_browser()
        await self.start_browser(**kwargs)

    @abstractmethod
    async def handle_exception(self, exception: Exception) -> None:
        """
        Handle browser-specific exceptions.
        
        Args:
            exception: The exception to handle
        """
        pass

    @property
    def context(self) -> Optional[Any]:
        """Get the current browser context."""
        return self._context 