from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class RawLinkedInData:
    id: Optional[int] = None
    name_location_panel: Optional[str] = None
    about_panel: Optional[str] = None
    experience_panel: Optional[str] = None
    education_panel: Optional[str] = None
    scraped_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self):
        """Return a dictionary representation of the instance, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}