from typing import Any, Optional
import logging
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext
from .browser_manager import BrowserManager
from .exceptions import BrowserNotInitializedError

logger = logging.getLogger(__name__)

class PlaywrightBrowser(BrowserManager):
    """
    Playwright implementation of BrowserManager.
    Handles Playwright-specific browser operations.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        super().__init__()
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._storage_path = storage_path or Path.home() / '.linkedin_scraper' / 'state.json'
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)

    async def start_browser(self, **kwargs) -> None:
        """
        Start a Playwright browser instance with given configuration.
        
        Args:
            **kwargs: Configuration options for Playwright browser
                headless (bool): Whether to run browser in headless mode
                proxy (dict): Proxy configuration
                user_agent (str): Custom user agent string
                restore_session (bool): Whether to restore previous session
        """
        if self._browser and not self._browser.is_closed():
            return

        self._playwright = await async_playwright().start()
        
        browser_type = kwargs.get('browser_type', 'chromium')
        browser_instance = getattr(self._playwright, browser_type)

        launch_options = {
            'headless': kwargs.get('headless', False),
        }

        if proxy := kwargs.get('proxy'):
            launch_options['proxy'] = proxy

        self._browser = await browser_instance.launch(**launch_options)
        
        # Create context with options
        context_options = {}
        if user_agent := kwargs.get('user_agent'):
            context_options['user_agent'] = user_agent

        # Restore session if requested and available
        if kwargs.get('restore_session', True) and self._storage_path.exists():
            context_options['storage_state'] = str(self._storage_path)

        self._context = await self._browser.new_context(**context_options)
        self._is_initialized = True

    async def close_browser(self) -> None:
        """Close the Playwright browser and save session state."""
        if self._context:
            # Save session state before closing
            try:
                await self._context.storage_state(path=str(self._storage_path))
            except Exception as e:
                logger.error(f"Failed to save session state: {str(e)}")
            
            await self._context.close()
            self._context = None

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

        self._is_initialized = False

    def is_browser_open(self) -> bool:
        """Check if Playwright browser is open and ready."""
        return bool(self._browser and not self._browser.is_closed())

    def get_browser_instance(self) -> Browser:
        """
        Get the current Playwright browser instance.
        
        Returns:
            Browser: The Playwright browser instance
        
        Raises:
            BrowserNotInitializedError: If browser hasn't been started
        """
        if not self._browser or self._browser.is_closed():
            raise BrowserNotInitializedError("Browser not initialized or closed")
        return self._browser

    async def handle_exception(self, exception: Exception) -> None:
        """
        Handle Playwright-specific exceptions.
        
        Args:
            exception: The exception to handle
        """
        if "Browser closed" in str(exception):
            await self.restart_browser()
        else:
            raise exception

    async def clear_session(self) -> None:
        """Clear stored session data."""
        try:
            if self._storage_path.exists():
                self._storage_path.unlink()
        except Exception as e:
            logger.error(f"Failed to clear session: {str(e)}") 