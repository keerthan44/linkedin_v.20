import logging
import asyncio
from typing import Optional, Any, Dict

from ..browser.playwright_scraper import PlaywrightScraper
from ..browser.exceptions import BrowserError
from ..selectors.linkedin_selectors import LinkedInSelectors
from .linkedin_session_interface import LinkedInSessionInterface, ScraperInterface

logger = logging.getLogger(__name__)

class PlaywrightLinkedInSession(LinkedInSessionInterface):
    """
    Manages LinkedIn session using Playwright.
    Handles browser lifecycle, authentication, and session state.
    """

    def __init__(self):
        self._scraper = PlaywrightScraper()  # Initialize without browser
        self.selectors = LinkedInSelectors()
        self._is_logged_in = False

    async def initialize(self, **kwargs) -> None:
        """Initialize browser and session."""
        try:
            await self._scraper.launch_browser(
                headless=False,
            )
            await self._scraper.new_page()
        except Exception as e:
            logger.error(f"Failed to initialize session: {str(e)}")
            raise

    async def close(self) -> None:
        """Close browser and cleanup resources."""
        await self._scraper.close_browser()
        self._is_logged_in = False

    async def login(self, username: str, password: str) -> bool:
        """Handle LinkedIn login process."""
        try:
            # First check if we're already logged in by trying to access the feed
            await self._scraper.navigate_to('https://www.linkedin.com/feed')
            await asyncio.sleep(2)  # Wait for potential redirect
            
            # Get current URL to check if we were redirected to feed
            current_url = await self._scraper.get_current_url()
            if 'linkedin.com/feed' in current_url:
                logger.info("Using existing LinkedIn session")
                self._is_logged_in = True
                return True

            # If not logged in, proceed with login
            logger.info("No existing session found, logging in...")
            await self._scraper.navigate_to('https://www.linkedin.com/login')
            await self._scraper.fill_input(self.selectors.USERNAME_INPUT, username)
            await self._scraper.fill_input(self.selectors.PASSWORD_INPUT, password)
            await self._scraper.click_element(self.selectors.LOGIN_BUTTON)
            await self._scraper.wait_for_navigation()

            # Validate login
            is_valid = await self.validate_session()
            if is_valid:
                # Save state immediately after successful login
                await self._scraper.save_storage_state()
                logger.info("Successfully logged in and saved session")
                self._is_logged_in = True
            return is_valid

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    async def validate_session(self) -> bool:
        """Check if we're still logged into LinkedIn."""
        try:
            # Check for elements that indicate we're logged in
            is_valid = await self._scraper.is_element_visible(self.selectors.LOGGED_IN_INDICATOR)
            self._is_logged_in = is_valid
            return is_valid
        except Exception as e:
            logger.error(f"Session validation failed: {str(e)}")
            return False

    def get_scraper(self) -> ScraperInterface:
        """Get the scraper instance."""
        return self._scraper

    def get_browser(self) -> Any:
        """Get the browser instance."""
        return self._scraper._browser

    def is_logged_in(self) -> bool:
        """Check if currently logged in."""
        return self._is_logged_in 