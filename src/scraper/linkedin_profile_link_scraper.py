import logging
import asyncio
from typing import List, Optional, Dict
import re
from urllib.parse import urlparse, urljoin
from ..browser.exceptions import BrowserError
from ..session.linkedin_session_interface import LinkedInSessionInterface
from ..selectors.linkedin_selectors import SearchSelectors

logger = logging.getLogger(__name__)

class LinkedInProfileLinkScraper:
    """
    Scraper for finding and extracting LinkedIn profile URLs.
    Can extract from search results, company pages, connection lists, etc.
    """

    def __init__(self, session: LinkedInSessionInterface):
        self._scraper = session.get_scraper()
        self.selectors = SearchSelectors()

    def _clean_profile_url(self, url: str) -> str:
        """
        Clean profile URL by removing query parameters and fragments.
        
        Args:
            url: Raw LinkedIn profile URL
            
        Returns:
            Cleaned URL containing only the path
        """
        try:
            parsed = urlparse(url)
            # Reconstruct URL with only scheme, netloc and path
            return urljoin(
                f"{parsed.scheme}://{parsed.netloc}",
                parsed.path.rstrip('/')  # Remove trailing slash
            )
        except Exception:
            return url

    async def get_profile_links_from_search(self, search_query: str, num_pages: int = 1) -> List[str]:
        """
        Get profile links from LinkedIn search results.
        
        Args:
            search_query: Search term to find profiles
            num_pages: Number of pages to scrape (default: 1)
            
        Returns:
            List of profile URLs
        """
        try:
            # Navigate to search results
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}"
            await self._scraper.navigate_to(search_url)
            
            profile_links = set()
            for page in range(num_pages):
                # Extract links from current page
                await self._scraper.wait_for_selector(self.selectors.SEARCH_RESULTS)
                await self._scraper.scroll_to_bottom()
                await asyncio.sleep(2)  # Wait for content to load

                # Get profile links
                links = await self._scraper.evaluate_script(f"""
                    Array.from(document.querySelectorAll('{self.selectors.PROFILE_LINKS}')).map(e => e.href)
                """)

                # Get and filter out insight links
                insights_links = await self._scraper.evaluate_script(f"""
                    Array.from(document.querySelectorAll('{self.selectors.INSIGHTS_LINKS}')).map(e => e.href)
                """)

                # Filter, validate and clean links
                filtered_links = [
                    self._clean_profile_url(link)
                    for link in links 
                    if (link not in insights_links and 
                        "linkedin.com/in/" in link and
                        "SHARED_CONNECTIONS_CANNED_SEARCH" not in link)
                ]
                profile_links.update(filtered_links)
                
                # Go to next page if needed
                if page < num_pages - 1:
                    next_button = await self._scraper.is_element_visible(self.selectors.NEXT_BUTTON)
                    if next_button:
                        await self._scraper.click_element(self.selectors.NEXT_BUTTON)
                        await asyncio.sleep(2)  # Wait for page load
                    else:
                        break

            return list(profile_links)

        except Exception as e:
            logger.error(f"Failed to get profile links: {str(e)}")
            return []

    async def get_profile_links_from_company(self, company_url: str, max_results: Optional[int] = None) -> List[str]:
        """Get profile links from a company's employee list."""
        # Implementation for company employee scraping
        pass

    async def get_profile_links_from_connections(self, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get profile links from user's connection list.
        
        Args:
            max_results: Optional maximum number of connections to retrieve
            
        Returns:
            List of dictionaries containing connection details:
            {
                'name': str,
                'occupation': str,
                'url': str
            }
        """
        try:
            # Navigate to connections page
            await self._scraper.navigate_to("https://www.linkedin.com/mynetwork/invite-connect/connections/")
            await self._scraper.wait_for_selector(self.selectors.CONNECTIONS_CONTAINER)
            
            connections = []
            processed_urls = set()
            
            while True:
                # Get all connection cards
                cards = await self._scraper.evaluate_script(f"""
                    Array.from(document.querySelectorAll('{self.selectors.CONNECTION_CARD}')).map(card => ({{
                        name: card.querySelector('{self.selectors.CONNECTION_NAME}')?.innerText.trim(),
                        occupation: card.querySelector('{self.selectors.CONNECTION_OCCUPATION}')?.innerText.trim(),
                        url: card.querySelector('{self.selectors.CONNECTION_LINK}')?.href
                    }}))
                """)
                
                # Process new connections
                for card in cards:
                    if card['url'] and card['url'] not in processed_urls:
                        processed_urls.add(card['url'])
                        connections.append({
                            'name': card['name'],
                            'occupation': card['occupation'],
                            'url': self._clean_profile_url(card['url'])
                        })
                
                # Check if we've reached the desired number of results
                if max_results and len(connections) >= max_results:
                    connections = connections[:max_results]
                    break
                
                # Scroll to load more
                last_height = await self._scraper.evaluate_script("document.body.scrollHeight")
                await self._scraper.scroll_to_bottom()
                await asyncio.sleep(2)  # Wait for content to load
                
                # Check if we've reached the bottom
                new_height = await self._scraper.evaluate_script("document.body.scrollHeight")
                if new_height == last_height:
                    break
            
            logger.info(f"Found {len(connections)} connections")
            return connections

        except Exception as e:
            logger.error(f"Failed to get connections: {str(e)}")
            return [] 