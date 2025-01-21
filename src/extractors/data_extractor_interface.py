from abc import ABC, abstractmethod
from typing import Dict, Any, List

class DataExtractorInterface(ABC):
    """Interface for extracting data from LinkedIn profile HTML."""

    @abstractmethod
    async def extract_name(self, intro_panel: str) -> str:
        """Extract name from profile intro panel."""
        pass

    @abstractmethod
    async def extract_location(self, intro_panel: str) -> str:
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