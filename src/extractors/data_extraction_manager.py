from typing import Dict, Any, Optional
import logging

from .data_extractor_interface import DataExtractorInterface
from .hardcoded_extractor import HardcodedDataExtractor
from ..browser.scraper_interface import ScraperInterface

logger = logging.getLogger(__name__)

class DataExtractionManager:
    """
    Manages data extraction from LinkedIn pages using different extractors.
    """

    def __init__(self, scraper: ScraperInterface, extractor: Optional[DataExtractorInterface] = None):
        self._extractor = extractor or HardcodedDataExtractor(scraper)

    async def extract_profile_data(self, html: str = "") -> Dict[str, Any]:
        """
        Extract all profile data using the configured extractor.
        
        Args:
            html: Not used with ScraperInterface
            
        Returns:
            Dict containing all extracted profile data
        """
        try:
            return {
                'name': await self._extractor.extract_name(html),
                'location': await self._extractor.extract_location(html),
                'experience': await self._extractor.extract_experience(html),
                'education': await self._extractor.extract_education(html),
            }
        except Exception as e:
            logger.error(f"Failed to extract profile data: {str(e)}")
            return {} 