from datetime import datetime
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class DateNormalizer:
    """
    A class responsible for normalizing dates from various formats to a standardized format.
    """
    
    DEFAULT_OUTPUT_FORMAT = '%Y-%m-%d'
    
    def __init__(self):
        self._formats: List[str] = [
            '%b %Y',      # Aug 2023
            '%B %Y',      # August 2023
            '%Y',         # 2023
            '%b %d, %Y',  # Aug 1, 2023
            '%B %d, %Y'   # August 1, 2023
        ]
    
    def add_format(self, date_format: str) -> None:
        """
        Add a new date format to the supported formats.
        
        Args:
            date_format (str): A strftime-compatible format string
        """
        if date_format not in self._formats:
            self._formats.append(date_format)
    
    def normalize(self, date_str: str) -> Optional[str]:
        """
        Convert various date formats to YYYY-MM-DD
        
        Args:
            date_str (str): Date string in various formats (e.g., 'Aug 2023', 'August 2023', '2023')
            
        Returns:
            Optional[str]: Normalized date in YYYY-MM-DD format, or None if conversion fails
        """
        if not date_str or date_str.lower() == 'present':
            return None
            
        try:
            # Remove any extra whitespace
            date_str = date_str.strip()
            
            # Try each format until one works
            for fmt in self._formats:
                try:
                    return datetime.strptime(date_str, fmt).strftime(self.DEFAULT_OUTPUT_FORMAT)
                except ValueError:
                    continue
                    
            # If no format matches, return None
            return None
            
        except Exception as e:
            logger.error(f"Error normalizing date {date_str}: {e}")
            return None

# Create a singleton instance for general use
default_normalizer = DateNormalizer()

def normalize_date(date_str: str) -> Optional[str]:
    """
    Convenience function that uses the default normalizer.
    
    Args:
        date_str (str): Date string to normalize
        
    Returns:
        Optional[str]: Normalized date string or None
    """
    return default_normalizer.normalize(date_str) 