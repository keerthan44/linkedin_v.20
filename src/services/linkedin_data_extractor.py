import logging
from src.repository.supabase_repository import SupabaseRepository
from src.extractors.hardcoded_extractor import HardcodedDataExtractor
from src.session.playwright_linkedin_session import PlaywrightLinkedInSession
from src.models.linkedin_about import LinkedInAbout
from src.models.linkedin_educations import LinkedInEducation
from src.models.linkedin_experiences import LinkedInExperience
from src.utils.vectorization_service import VectorizationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInDataExtractor:
    def __init__(self):
        self.repository = SupabaseRepository()
        self.session = PlaywrightLinkedInSession()  # Initialize the session
        self.vectorization_service = VectorizationService()  # Initialize the vectorization service
    
    async def initialize(self):
        await self.session.initialize()
        self.extractor = HardcodedDataExtractor(self.session.get_scraper())  # Pass the scraper to the extractor

    async def extract_and_process_profiles(self):
        """Retrieve unprocessed LinkedIn profiles and extract their data."""
        unprocessed_profiles = await self.repository.get_unprocessed_linkedin_profiles()
        
        if not unprocessed_profiles:
            logger.info("No unprocessed LinkedIn profiles found.")
            return
        
        for profile in unprocessed_profiles:
            # Fetch the raw data using raw_data_id
            raw_data = await self.repository.get_raw_linkedin_data(profile.raw_data_id)
            
            if raw_data:
                extracted_data = await self.extractor.extract(raw_data)  # Ensure this is awaited
                
                # Create LinkedInAbout instance
                about_data = LinkedInAbout(
                    id=None,  # Set to None for new entries
                    profile_id=profile.id,  # Use the profile ID
                    about_content=extracted_data.get("about", ""),  # Extract the about content
                    semantic_embedding=self.vectorization_service.vectorize_text(extracted_data.get('about', '')),  # Add any relevant data if available
                    created_at=None,  # Set to None for new entries
                    updated_at=None   # Set to None for new entries
                )
                
                
                # Upsert the about data
                success = await self.repository.upsert_linkedin_about(profile.id, about_data)
                if success:
                    logger.info(f"Successfully upserted about data for profile ID: {profile.id}")
                else:
                    logger.warning(f"Failed to upsert about data for profile ID: {profile.id}")

                # Handle education data
                education_list = extracted_data.get("education", [])
                for edu in education_list:
                    # Get or create the institution
                    institution_name = edu.get("institution_name", "")
                    institution = await self.repository.get_or_create_institution(institution_name)
                    
                    if institution:
                        # Create LinkedInEducation instance
                        education_data = LinkedInEducation(
                            profile_id=profile.id,  # Use the profile ID
                            institution_id=institution.id,  # Use the institution ID from the created or retrieved institution
                            degree=edu.get("degree", ""),
                            from_date=edu.get("from_date", ""),
                            to_date=edu.get("to_date", ""),
                            description=edu.get("description", ""),
                            semantic_embedding=self.vectorization_service.vectorize_text(edu.get('description', ''))
                        )
                        
                        # Upsert the education data
                        success = await self.repository.upsert_linkedin_educations(profile.id, education_data)
                        if success:
                            logger.info(f"Successfully upserted education data for profile ID: {profile.id}")
                        else:
                            logger.warning(f"Failed to upsert education data for profile ID: {profile.id}")
                    else:
                        logger.warning(f"Failed to retrieve or create institution for {institution_name}")

                # Handle experience data
                # experience_list = extracted_data.get("experience", [])
                # for exp in experience_list:
                #     # Get or create the institution for experience
                #     institution_name = exp.get("institution_name", "")
                #     institution = await self.repository.get_or_create_institution(institution_name)
                    
                #     if institution:
                #         # Create LinkedInExperience instance
                #         experience_data = LinkedInExperience(
                #             profile_id=profile.id,  # Use the profile ID
                #             institution_id=institution.id,  # Use the institution ID from the created or retrieved institution
                #             position_title=exp.get("position_title", ""),
                #             from_date=exp.get("to_date", ""),
                #             to_date=exp.get("from_date", ""),
                #             description=exp.get("description", ""),
                #         )
                        
                #         # Upsert the experience data
                #         success = await self.repository.upsert_linkedin_experience(profile.id, experience_data)
                #         if success:
                #             logger.info(f"Successfully upserted experience data for profile ID: {profile.id}")
                #         else:
                #             logger.warning(f"Failed to upsert experience data for profile ID: {profile.id}")
                #     else:
                #         logger.warning(f"Failed to retrieve or create institution for {institution_name}")

            else:
                logger.warning(f"No raw data found for profile ID: {profile.raw_data_id}") 