import asyncio
import logging
from pathlib import Path
import sys
import json
from typing import List

# Add parent directory to path to import scraper modules
sys.path.append(str(Path(__file__).parent.parent))

from src.session.playwright_linkedin_session import PlaywrightLinkedInSession
from src.services.linkedin_scraping_service import LinkedInScrapingService  # Import the service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def dump_profiles_to_database(profile_urls: List[str], username: str, password: str) -> None:
    """Scrape LinkedIn profiles and store data in the database."""
    # Initialize the LinkedIn scraping service
    scraping_service = LinkedInScrapingService()
    await scraping_service.initialize()  # Initialize the session

    try:
        # Scrape and store profiles using the service
        await scraping_service.scrape_and_store_profiles(profile_urls, username, password)

    except Exception as e:
        logger.error(f"An error occurred while dumping profiles: {str(e)}")
    
    finally:
        await scraping_service.session.close()  # Ensure the session is closed
        logger.info("Session closed")

async def main():
    # Example profile URLs
    profile_urls = [
        'https://www.linkedin.com/in/rohinrohin/',
    ]
    
    # LinkedIn credentials
    username = "a"  # Replace with your LinkedIn email
    password = "your_password"  # Replace with your LinkedIn password

    if not profile_urls:
        logger.error("No profile URLs found")
        return

    logger.info(f"Loaded {len(profile_urls)} profile URLs")
    
    # Dump profiles to database
    await dump_profiles_to_database(profile_urls, username, password)

if __name__ == "__main__":
    asyncio.run(main()) 