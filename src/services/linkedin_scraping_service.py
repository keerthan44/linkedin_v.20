import asyncio
import logging
from src.session.playwright_linkedin_session import PlaywrightLinkedInSession
from src.scraper.linkedin_people_scraper import LinkedInPeopleScraper
from src.repository.supabase_repository import SupabaseRepository
from src.models.raw_linkedin_data import RawLinkedInData
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInScrapingService:
    def __init__(self):
        self.session = PlaywrightLinkedInSession()
        self.people_scraper = None
        self.repository = SupabaseRepository()

    async def initialize(self):
        await self.session.initialize()
        self.people_scraper = LinkedInPeopleScraper(self.session)

    async def scrape_and_store_profiles(self, profile_urls: list, username: str, password: str) -> None:
        """Scrape LinkedIn profiles and store data in the database."""
        try:
            if not username or not password:
                logger.error("LinkedIn credentials not found")
                return
            
            logger.info("Logging in to LinkedIn...")
            if not await self.session.login(username, password):
                logger.error("Failed to login to LinkedIn")
                return
            
            # Process each profile URL
            for i, url in enumerate(profile_urls, 1):
                try:
                    logger.info(f"Processing profile {i}/{len(profile_urls)}: {url}")
                    
                    # First get the raw HTML using people scraper
                    raw_data = await self.people_scraper.scrape_profile(url)
                    
                    if not raw_data:
                        logger.error(f"Failed to get raw data for {url}")
                        continue
                    
                    # Save raw data for debugging
                    debug_file = f"debug_raw_data_{url.split('/')[-1]}.json"
                    try:
                        with open(debug_file, "w", encoding='utf-8') as f:
                            json.dump(raw_data, f, indent=2, ensure_ascii=False)
                        logger.info(f"Saved raw data to {debug_file}")
                    except Exception as e:
                        logger.error(f"Failed to save raw data: {str(e)}")
                    
                    # Upsert raw data into the database using the repository's method
                    await self.repository.insert_raw_data(url, RawLinkedInData(**raw_data))

                    logger.info(f"Successfully upserted data for: {url}")
                    
                    # Add a small delay between profiles
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Failed to extract data from {url}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
        
        finally:
            # Cleanup
            await self.session.close()
            logger.info("Session closed") 