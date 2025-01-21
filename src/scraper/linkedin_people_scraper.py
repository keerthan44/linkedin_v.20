import logging
from typing import Dict, Any
import asyncio
import random

from .base_scraper import BaseLinkedInScraper
from ..selectors.linkedin_selectors import PeopleSelectors
from ..browser.exceptions import BrowserError

logger = logging.getLogger(__name__)

class LinkedInPeopleScraper(BaseLinkedInScraper):
    """
    Specialized scraper for LinkedIn people/profile pages.
    Implements all abstract methods from BaseLinkedInScraper.
    """

    def __init__(self, session):
        super().__init__(session)
        self.selectors = PeopleSelectors()

    async def scrape_profile(self, profile_url: str) -> Dict[str, Any]:
        """
        Scrape a LinkedIn profile page.
        
        Args:
            profile_url: Full URL of the LinkedIn profile to scrape
            
        Returns:
            Dict containing the profile data
        """
        try:
            # Navigate to the profile
            await self._scraper.navigate_to(profile_url)
            await self._scraper.wait_for_selector(self.selectors.INTRO_PANEL)
            
            # Extract the data
            return await self.extract_data(profile_url, "profile")
            
        except BrowserError as e:
            logger.error(f"Failed to scrape profile {profile_url}: {str(e)}")
            return {}

    async def extract_data(self, profile_url: str, data_type: str) -> Dict[str, Any]:
        """Extract structured data from LinkedIn HTML."""
        if data_type == 'profile':
            return {
                'intro_panel': await self.get_intro_panel_html(),
                'experience_panel': await self.get_experience_html(profile_url),
                'education_panel': await self.get_education_html(profile_url),
            }
        raise ValueError(f"Unsupported data type: {data_type}")

    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate extracted profile data."""
        required_fields = ['intro_panel', 'experience', 'education']
        return all(field in data and data[field] for field in required_fields)

    async def get_intro_panel_html(self) -> str:
        """
        Get HTML content of the profile intro panel containing name and location.
        Returns raw HTML string of the intro section.
        """
        try:
            # Get the intro panel HTML
            intro_panel = await self._scraper.get_element_html(self.selectors.INTRO_PANEL)
            return intro_panel
        except BrowserError as e:
            logger.error(f"Failed to get intro panel HTML: {str(e)}")
            return ""

    async def get_experience_html(self, profile_url: str) -> str:
        """
        Get HTML content of the experience section.
        Opens experience section in a new page for direct access.
        """
        try:
            # Format the experience section URL
            experience_url = f"{profile_url}/details/experience/"
            
            # Create and navigate new page to experience section
            await self._scraper.new_page()
            await self._scraper.navigate_to(experience_url)
            
            # Wait specifically for the experience list container
            await self._scraper.wait_for_selector(self.selectors.EXPERIENCE_SECTION)
            
            # Wait for initial content load
            await asyncio.sleep(2)
            
            # Get page height and scroll to middle first
            page_height = await self._scraper.evaluate_script("document.body.scrollHeight")
            mid_height = page_height // 2
            
            # Scroll to middle and wait
            await self._scraper.scroll_to_position(mid_height)
            await asyncio.sleep(random.uniform(1, 2))
            
            # Scroll to bottom and wait
            await self._scraper.scroll_to_bottom()
            await asyncio.sleep(random.uniform(1, 2))

            # Get experience section HTML
            experience_html = await self._scraper.get_element_html(self.selectors.EXPERIENCE_SECTION)
            
            # Close the experience page
            await self._scraper.close_page()
            
            return experience_html

        except BrowserError as e:
            logger.error(f"Failed to get experience HTML: {str(e)}")
            # Make sure to close the page even if there's an error
            await self._scraper.close_page()
            return ""

    async def get_education_html(self, profile_url: str) -> str:
        """
        Get HTML content of the education section.
        Opens education section in a new page for direct access.
        """
        try:
            # Format the education section URL
            education_url = f"{profile_url}/details/education/"
            
            # Create and navigate new page to education section
            await self._scraper.new_page()
            await self._scraper.navigate_to(education_url)
            
            # Wait specifically for the education list container
            await self._scraper.wait_for_selector(self.selectors.EDUCATION_SECTION)
            
            # Wait for initial content load
            await asyncio.sleep(2)
            
            # Get page height and scroll to middle first
            page_height = await self._scraper.evaluate_script("document.body.scrollHeight")
            mid_height = page_height // 2
            
            # Scroll to middle and wait
            await self._scraper.scroll_to_position(mid_height)
            await asyncio.sleep(random.uniform(1, 2))
            
            # Scroll to bottom and wait
            await self._scraper.scroll_to_bottom()
            await asyncio.sleep(random.uniform(1, 2))

            # Get education section HTML
            education_html = await self._scraper.get_element_html(self.selectors.EDUCATION_SECTION)
            
            # Close the education page
            await self._scraper.close_page()
            
            return education_html

        except BrowserError as e:
            logger.error(f"Failed to get education HTML: {str(e)}")
            # Make sure to close the page even if there's an error
            await self._scraper.close_page()
            return "" 