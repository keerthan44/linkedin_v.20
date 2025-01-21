import asyncio
import logging
from pathlib import Path
import sys
import os

# Add parent directory to path to import scraper modules
sys.path.append(str(Path(__file__).parent.parent))

from src.session.playwright_linkedin_session import PlaywrightLinkedInSession
from src.scraper.linkedin_profile_link_scraper import LinkedInProfileLinkScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    # Initialize session
    session = PlaywrightLinkedInSession()
    await session.initialize()
    
    try:
        # Get credentials from environment or config
        username = "keerthan44@gmail.com"
        password = "Myself2002[]"
        
        if not username or not password:
            logger.error("LinkedIn credentials not found in environment variables")
            return
        
        # Login using session manager
        logger.info("Logging in to LinkedIn...")
        if not await session.login(username, password):
            logger.error("Failed to login to LinkedIn")
            return
        
        # Initialize profile link scraper with authenticated session
        link_scraper = LinkedInProfileLinkScraper(session)
        
        # Search parameters
        search_query = "software engineer"
        num_pages = 2
        
        # Extract profile links
        logger.info(f"Searching for profiles matching: {search_query}")
        profile_links = await link_scraper.get_profile_links_from_search(
            search_query=search_query,
            num_pages=num_pages
        )
        
        # Print results
        logger.info(f"Found {len(profile_links)} unique profile links:")
        for i, link in enumerate(profile_links, 1):
            logger.info(f"{i}. {link}")
            
        # Save links to file
        output_file = "profile_links.txt"
        with open(output_file, "w") as f:
            for link in profile_links:
                f.write(f"{link}\n")
        logger.info(f"Saved profile links to {output_file}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    
    finally:
        # Cleanup
        await session.close()
        logger.info("Session closed")

if __name__ == "__main__":
    asyncio.run(main()) 