from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class LinkedInProfile:
    id: Optional[int] = None
    profile_url: str = ""
    name: Optional[str] = None
    raw_data_id: Optional[int] = None
    processed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_processed: Optional[bool] = False 

    def to_dict(self):
        """Return a dictionary representation of the instance, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None} 