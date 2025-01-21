import asyncio
import logging
from pathlib import Path
import sys
import json
from typing import List, Dict, Any

# Add parent directory to path to import scraper modules
sys.path.append(str(Path(__file__).parent.parent))

from src.session.playwright_linkedin_session import PlaywrightLinkedInSession
from src.extractors.hardcoded_extractor import HardcodedDataExtractor
from src.scraper.linkedin_people_scraper import LinkedInPeopleScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def extract_profiles(profile_urls: List[str]) -> List[Dict[str, Any]]:
    """Extract data from multiple LinkedIn profiles."""
    # Initialize session
    session = PlaywrightLinkedInSession()
    await session.initialize()
    
    profiles_data = []
    
    try:
        # Login
        username = "keerthan44@gmail.com"
        password = "Myself2002[]"
        
        if not username or not password:
            logger.error("LinkedIn credentials not found")
            return profiles_data
        
        logger.info("Logging in to LinkedIn...")
        if not await session.login(username, password):
            logger.error("Failed to login to LinkedIn")
            return profiles_data
        
        # Initialize scrapers and extractors with the scraper from session
        scraper = session.get_scraper()
        people_scraper = LinkedInPeopleScraper(session)
        extractor = HardcodedDataExtractor(scraper)  # Pass scraper instead of session
        
        # Process each profile URL
        for i, url in enumerate(profile_urls, 1):
            try:
                logger.info(f"Processing profile {i}/{len(profile_urls)}: {url}")
                
                # First get the raw HTML using people scraper
                raw_data = await people_scraper.scrape_profile(url)
                
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
                
                # Then extract structured data using hardcoded extractor
                profile_data = {
                    'url': url,
                    'name': await extractor.extract_name(raw_data.get('intro_panel', '')),
                    'location': await extractor.extract_location(raw_data.get('intro_panel', '')),
                    'experience': await extractor.extract_experience(raw_data.get('experience_panel', '')),
                    'education': await extractor.extract_education(raw_data.get('education_panel', ''))
                }
                
                profiles_data.append(profile_data)
                logger.info(f"Successfully extracted data for: {profile_data.get('name', 'Unknown')}")
                
                # Add a small delay between profiles
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to extract data from {url}: {str(e)}")
                continue

        # Save all profiles data to JSON
        output_file = "profiles_data.json"
        with open(output_file, "w") as f:
            json.dump(profiles_data, f, indent=2)
        logger.info(f"Saved {len(profiles_data)} profiles to {output_file}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    
    finally:
        # Cleanup
        await session.close()
        logger.info("Session closed")
    
    return profiles_data

async def main():
    # Example profile URLs
    profile_urls = ['https://www.linkedin.com/in/rohinrohin']
            
    if not profile_urls:
        logger.error("No profile URLs found")
        return
            
    logger.info(f"Loaded {len(profile_urls)} profile URLs")
    
    # Extract data from all profiles
    profiles_data = await extract_profiles(profile_urls)
    
    # Print summary
    logger.info(f"\nExtraction Summary:")
    logger.info(f"Total profiles processed: {len(profiles_data)}")
    logger.info(f"Successful extractions: {len([p for p in profiles_data if p.get('name')])}")
    logger.info(f"Failed extractions: {len(profile_urls) - len([p for p in profiles_data if p.get('name')])}")

if __name__ == "__main__":
    asyncio.run(main()) 