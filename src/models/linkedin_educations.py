from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from langchain_community.embeddings import HuggingFaceEmbeddings


@dataclass
class LinkedInEducation:
    id: Optional[int] = None
    profile_id: Optional[int] = None
    institution_id: Optional[int] = None
    degree: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    description: Optional[str] = None
    semantic_embedding: Optional[HuggingFaceEmbeddings] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self):
        """Return a dictionary representation of the instance, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}