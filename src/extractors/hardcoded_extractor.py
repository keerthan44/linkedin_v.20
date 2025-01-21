from typing import Dict, Any, List, Optional
import logging
from ..browser.scraper_interface import ScraperInterface
from ..selectors.linkedin_selectors import PeopleSelectors
from ..browser.exceptions import BrowserError
import asyncio
from datetime import datetime

from .data_extractor_interface import DataExtractorInterface

logger = logging.getLogger(__name__)

class HardcodedDataExtractor(DataExtractorInterface):
    """
    Data extractor using hardcoded selectors and ScraperInterface.
    """

    def __init__(self, scraper: ScraperInterface):
        self.selectors = PeopleSelectors()
        self._scraper = scraper
        self._page = None

    async def _init_page(self) -> None:
        """Initialize a new page if not exists."""
        if not self._page:
            self._page = await self._scraper.new_page()

    async def _get_element_text(self, selector: str) -> str:
        """Get text from element using the page."""
        element = await self._page.wait_for_selector(selector)
        if not element:
            return ""
        text = await element.text_content()
        return text.strip() if text else ""

    async def _evaluate_script(self, script: str) -> Any:
        """Evaluate JavaScript on the page."""
        return await self._page.evaluate(script)

    async def extract_name(self, intro_panel: str) -> str:
        """Extract name from profile intro panel."""
        page = None
        try:
            page = await self._scraper.new_page()
            await page.set_content(intro_panel)
            element = await page.wait_for_selector(self.selectors.NAME)
            if not element:
                return ""
            text = await element.text_content()
            return text.strip() if text else ""
        except Exception as e:
            logger.error(f"Failed to extract name: {str(e)}")
            return ""
        finally:
            if page:
                await page.close()

    async def extract_location(self, intro_panel: str) -> str:
        """Extract location from profile intro panel."""
        page = None
        try:
            page = await self._scraper.new_page()
            await page.set_content(intro_panel)
            element = await page.wait_for_selector(self.selectors.LOCATION)
            if not element:
                return ""
            text = await element.text_content()
            return text.strip() if text else ""
        except Exception as e:
            logger.error(f"Failed to extract location: {str(e)}")
            return ""
        finally:
            if page:
                await page.close()

    async def extract_experience(self, experience_panel: str) -> List[Dict[str, str]]:
        """Extract work experience information."""
        page = None
        try:
            page = await self._scraper.new_page()
            await page.set_content(experience_panel)
            # input()  # Debug pause
            
            # Get all positions directly since we already have the container HTML
            positions = await page.locator("ul").locator('> .pvs-list__paged-list-item').all()
            
            # Extract all spans text
            all_spans_text = []
            for position in positions:
                spans = await position.locator('span[aria-hidden="true"]').all()
                span_texts = [await span.inner_text() for span in spans]
                all_spans_text.append(span_texts)

            # Process the raw experience data
            profile_experience = []
            
            for exp in all_spans_text:
                # Initialize the current experience with all fields set to None
                current_experience = {
                    "position_title": None,
                    "institution_name": None,
                    "duration": None,
                    "from_date": None,
                    "to_date": None,
                    "location": None,
                    "description": None,
                }

                for idx, text in enumerate(exp):
                    # Detect if it's a position title
                    if idx == 0 and text:
                        current_experience["position_title"] = text

                    # Detect if it's an institution name or company
                    elif idx == 1 and text:
                        current_experience["institution_name"] = text

                    # Detect the duration (it will contain date-like values like 'Sep 2024 - Present')
                    elif " - " in text and ('Present' in text or 'mos' in text):
                        current_experience["duration"] = text
                        dates = text.split(' · ')[0].split(' - ')
                        current_experience["from_date"] = self._normalize_date(dates[0])
                        current_experience["to_date"] = self._normalize_date(dates[1])

                    # Detect if it's a location (e.g., city and country)
                    elif '·' in text and len(text.split('·')) > 1:
                        current_experience["location"] = text.split('·')[0].strip()

                    # Detect if it's a description (it could be the last element, e.g., skills or job details)
                    elif idx == len(exp) - 1 and text:
                        current_experience["description"] = text

                # Once the experience is complete, add to the profile
                profile_experience.append(current_experience)

            return profile_experience

        except Exception as e:
            logger.error(f"Failed to extract experience: {str(e)}")
            return []
        finally:
            if page:
                await page.close()

    def _normalize_date(self, date_str):
        """Convert various date formats to YYYY-MM-DD"""
        if not date_str or date_str == 'Present':
            return None
            
        try:
            # Remove any extra whitespace
            date_str = date_str.strip()
            
            # Handle 'Present' case
            if date_str.lower() == 'present':
                return None
                
            # Try to parse common LinkedIn date formats
            formats = [
                '%b %Y',      # Aug 2023
                '%B %Y',      # August 2023
                '%Y',         # 2023
                '%b %d, %Y',  # Aug 1, 2023
                '%B %d, %Y'   # August 1, 2023
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
                    
            # If no format matches, return None
            return None
            
        except Exception as e:
            logger.error(f"Error normalizing date {date_str}: {e}")
            return None
    async def extract_education(self, education_panel: str) -> List[Dict[str, str]]:
        """Extract education information."""
        page = None
        try:
            page = await self._scraper.new_page()
            await page.set_content(education_panel)
            
            # Initialize the list to store education data
            educations_data = []
            
            # Loop through each education item
            for position in await page.query_selector_all(".pvs-list__paged-list-item"):
                position = await position.query_selector("div[data-view-name='profile-component-entity']")
                details = await position.query_selector_all("> *")
                institution_logo_elem, position_details = details
                
                # Fetch institution URL - Fix the chained async calls
                url_elem = await institution_logo_elem.query_selector("*")
                institution_linkedin_url = await url_elem.get_attribute("href") if url_elem else None
                
                # Fetch position details
                position_details_list = await position_details.query_selector_all("> *")
                position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
                position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
                
                # Extract data from outer positions
                summary_container = await position_summary_details.query_selector("*")
                outer_positions = await summary_container.query_selector_all("> *") if summary_container else []
                
                # Get institution name
                name_elem = await outer_positions[0].query_selector("span") if outer_positions else None
                institution_name = await name_elem.text_content() if name_elem else ""
                institution_name = institution_name.strip()
                
                # Get degree
                degree = None
                if len(outer_positions) > 1:
                    degree_elem = await outer_positions[1].query_selector("span")
                    if degree_elem:
                        degree = await degree_elem.text_content()
                        degree = degree.strip()

                # Get dates
                from_date = None
                to_date = None
                if len(outer_positions) > 2:
                    times_elem = await outer_positions[2].query_selector("span")
                    if times_elem:
                        times = await times_elem.text_content()
                        times = times.strip()
                        if times != "":
                            time_parts = times.split(" ")
                            if len(time_parts) > 3:
                                from_date = self._normalize_date(time_parts[time_parts.index("-") - 1])
                                to_date = self._normalize_date(time_parts[-1])
                            else:
                                from_date = self._normalize_date(time_parts[0])
                                to_date = self._normalize_date(time_parts[-1])

                # Get description
                description = ""
                if position_summary_text:
                    see_more_button = await position_summary_text.query_selector("text=…see more")
                    if see_more_button:
                        await see_more_button.click()
                        await page.wait_for_timeout(1000)  # Wait for the text to expand
                        expanded_text = await position_summary_text.query_selector("span")
                        if expanded_text:
                            description = await expanded_text.text_content()
                            description = description.strip()
                    else:
                        text_elem = await position_summary_text.query_selector("span")
                        if text_elem:
                            description = await text_elem.text_content()
                            description = description.strip()
                
                # Create the education dictionary
                education_data = {
                    "from_date": from_date,
                    "to_date": to_date,
                    "description": description,
                    "degree": degree,
                    "institution_name": institution_name,
                    "linkedin_url": institution_linkedin_url
                }
                
                # Add the education data to the list
                educations_data.append(education_data)

            return educations_data

        except Exception as e:
            logger.error(f"Failed to extract education: {str(e)}")
            return []
        finally:
            if page:
                await page.close()

    async def __del__(self):
        """Cleanup resources."""
        if self._page:
            await self._page.close()
            self._page = None
