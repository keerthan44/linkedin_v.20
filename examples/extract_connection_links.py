import asyncio
import logging
from pathlib import Path
import sys
import json

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
        # Get credentials
        username = "keerthan44@gmail.com"
        password = "Myself2002[]"
        
        if not username or not password:
            logger.error("LinkedIn credentials not found")
            return
        
        # Login using session manager
        logger.info("Logging in to LinkedIn...")
        if not await session.login(username, password):
            logger.error("Failed to login to LinkedIn")
            return
        
        # Initialize profile link scraper
        link_scraper = LinkedInProfileLinkScraper(session)
        
        # Extract connections (limit to first 50 for example)
        logger.info("Extracting connections...")
        connections = await link_scraper.get_profile_links_from_connections(max_results=50)
        
        # Print results
        logger.info(f"Found {len(connections)} connections")
        for i, conn in enumerate(connections, 1):
            logger.info(f"{i}. {conn['name']} - {conn['occupation']}")
            logger.info(f"   Profile: {conn['url']}")
            logger.info("---")
            
        # Save connections to file
        output_file = "connections.json"
        with open(output_file, "w") as f:
            json.dump(connections, f, indent=2)
        logger.info(f"Saved connections to {output_file}")

        # Also save just the URLs to a text file
        urls_file = "connection_urls.txt"
        with open(urls_file, "w") as f:
            for conn in connections:
                f.write(f"{conn['url']}\n")
        logger.info(f"Saved connection URLs to {urls_file}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    
    finally:
        # Cleanup
        await session.close()
        logger.info("Session closed")

if __name__ == "__main__":
    asyncio.run(main()) 