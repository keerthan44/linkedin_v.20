import asyncio
import sys
from pathlib import Path

# Add the parent directory of 'src' to the system path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.services.linkedin_data_extractor import LinkedInDataExtractor

async def main():
    extractor_service = LinkedInDataExtractor()
    await extractor_service.initialize()  # Ensure the session is initialized
    await extractor_service.extract_and_process_profiles()

if __name__ == "__main__":
    asyncio.run(main()) 