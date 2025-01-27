from abc import ABC, abstractmethod
from typing import Dict, Any, List
from ..models.raw_linkedin_data import RawLinkedInData

class DataExtractorInterface(ABC):
    """Interface for extracting data from LinkedIn profile HTML."""

    @abstractmethod
    async def extract_name(self, name_location_panel: str) -> str:
        """Extract name from profile intro panel."""
        pass

    @abstractmethod
    async def extract_title(self, name_location_panel: str) -> str:
        """Extract title from profile intro panel."""
        pass

    @abstractmethod
    async def extract_location(self, name_location_panel: str) -> str:
        """Extract location from profile intro panel."""
        pass

    @abstractmethod
    async def extract_experience(self, experience_panel: str) -> List[Dict[str, str]]:
        """Extract work experience information."""
        pass

    @abstractmethod
    async def extract_education(self, education_panel: str) -> List[Dict[str, str]]:
        """Extract education information."""
        pass

    @abstractmethod
    async def extract_about(self, about_panel: str) -> str:
        """Extract about section from profile."""
        pass 


    @abstractmethod
    async def extract(self, raw_data: RawLinkedInData):
        """Extract about section from profile."""
        pass 