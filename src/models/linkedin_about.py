from dataclasses import dataclass
from typing import Optional
from langchain_community.embeddings import HuggingFaceEmbeddings

@dataclass
class LinkedInAbout:
    id: Optional[int] = None
    profile_id: Optional[int] = None
    about_content: Optional[str] = None
    semantic_embedding: Optional[HuggingFaceEmbeddings] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self):
        """Return a dictionary representation of the instance, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}