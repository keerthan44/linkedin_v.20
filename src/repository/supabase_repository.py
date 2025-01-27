import os
import logging
from supabase import create_client, Client
from typing import Dict, Any, List
from .repository_interface import RepositoryInterface
from ..models.linkedin_about import LinkedInAbout
from ..models.linkedin_profiles import LinkedInProfile
from ..models.linkedin_experiences import LinkedInExperience
from ..models.linkedin_educations import LinkedInEducation
from ..models.institutions import Institution
from ..models.raw_linkedin_data import RawLinkedInData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseRepository(RepositoryInterface):
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL", "https://czfwylcshockfrprlcij.supabase.co")
        supabase_key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN6Znd5bGNzaG9ja2ZycHJsY2lqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzMzNzQ4MTksImV4cCI6MjA0ODk1MDgxOX0.FpuzOfgml9vkVRz1C4rMiSeDkCUZbptDjfZn9bMq7LI")
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and key must be set in environment variables")
        self.client: Client = create_client(supabase_url, supabase_key)

    

    async def insert_raw_data(self, profile_url: str, raw_data: RawLinkedInData) -> None:
        """Insert raw LinkedIn data into the database after checking if the profile exists."""
        try:
            # Check if the profile already exists
            profile_response = self.client.table("linkedin_profiles").select("id").eq("profile_url", profile_url).execute()
            
            if profile_response.data:
                logger.warning(f"Profile with URL {profile_url} already exists. Skipping insertion.")
                return
            
            # Check if raw_data is None
            if raw_data is None:
                logger.error("Raw data is None, skipping insertion.")
                return
            
            # Insert into raw_linkedin_data using the to_dict method
            response = self.client.table("raw_linkedin_data").insert(raw_data.to_dict()).execute()
            linkedin_raw_data_id = response.data[0]['id']

            # Prepare profile data for insertion
            profile_data = {
                "profile_url": profile_url,
                "raw_data_id": linkedin_raw_data_id,
                "is_processed": False  # Set to false initially
            }

            # Insert into linkedin_profiles
            profile_response = await self.insert_linkedin_profile(LinkedInProfile(**profile_data))

            if not profile_response:
                self.client.table("raw_linkedin_data").delete().eq("id", linkedin_raw_data_id).execute()
                logger.error("Failed to insert profile data, raw data deleted.")
                raise Exception("Failed to insert profile data.")

        except Exception as e:
            logger.error(f"Error inserting raw data: {str(e)}")
            if 'response' in locals() and response.data:
                self.client.table("raw_linkedin_data").delete().eq("id", response.data[0]['id']).execute()

    async def insert_linkedin_profile(self, profile_data: LinkedInProfile) -> bool:
        """Insert a LinkedIn profile into the database."""
        try:
            # Insert the profile data and capture the response
            response = self.client.table("linkedin_profiles").insert(profile_data.to_dict()).execute()

            # Get the generated ID from the response
            profile = response.data[0]  # Assuming the response returns a list of inserted records

            return True

        except Exception as e:
            logger.error(f"Error inserting profile data: {str(e)}")
            raise

    async def get_unprocessed_linkedin_profiles(self) -> List[LinkedInProfile]:
        """Retrieve all LinkedIn profiles where is_processed is False."""
        try:
            response = self.client.table("linkedin_profiles").select("*").eq("is_processed", False).execute()
            
            if response.data:
                return [LinkedInProfile(**profile) for profile in response.data]
            
            logger.info("No unprocessed LinkedIn profiles found.")
            return []

        except Exception as e:
            logger.error(f"Error retrieving unprocessed LinkedIn profiles: {str(e)}")
            return []

    async def get_raw_linkedin_data(self, raw_data_id: int) -> RawLinkedInData:
        """Retrieve raw LinkedIn data by ID."""
        try:
            response = self.client.table("raw_linkedin_data").select("*").eq("id", raw_data_id).execute()
            
            if response.data:
                return RawLinkedInData(**response.data[0])
            
            logger.info(f"No raw data found for ID: {raw_data_id}")
            return None

        except Exception as e:
            logger.error(f"Error retrieving raw LinkedIn data: {str(e)}")
            return None

    async def get_or_create_institution(self, institution_name: str) -> Institution:
        """Retrieve an institution by name or create it if it doesn't exist."""
        try:
            # Check if the institution already exists
            response = self.client.table("institutions").select("*").eq("name", institution_name).execute()
            
            if response.data:
                # Institution exists, return it
                return Institution(**response.data[0])
            
            # Institution does not exist, create it
            new_institution_data = {
                "name": institution_name,
                "type": None,  # You can set this to a default value or pass it as an argument
            }
            
            create_response = self.client.table("institutions").insert(new_institution_data).execute()
            
            if create_response.data:
                return Institution(**create_response.data[0])
            
            logger.error("Failed to create institution.")
            return None

        except Exception as e:
            logger.error(f"Error retrieving or creating institution: {str(e)}")
            return None

    async def upsert_linkedin_about(self, profile_id: int, about_data: LinkedInAbout) -> bool:
        """Upsert LinkedIn about data using profile_id."""
        try:
            # Prepare the data for upsert
            about_data_dict = about_data.to_dict()  # Assuming LinkedInAbout has a to_dict method
            about_data_dict['profile_id'] = profile_id  # Ensure profile_id is included

            # Perform the upsert operation
            response = self.client.table("linkedin_about").upsert(about_data_dict, on_conflict=["profile_id"]).execute()

            if response.data:
                logger.info(f"Successfully upserted about data for profile ID: {profile_id}")
                return True
            
            logger.error("Failed to upsert about data.")
            return False

        except Exception as e:
            logger.error(f"Error upserting LinkedIn about data: {str(e)}")
            return False

    async def upsert_linkedin_educations(self, profile_id: int, education_data: LinkedInEducation) -> bool:
        """Insert or update LinkedIn education data using profile_id and institution_id."""
        try:
            # Prepare the data for insertion
            education_data_dict = education_data.to_dict()  # Assuming LinkedInEducation has a to_dict method
            education_data_dict['profile_id'] = profile_id  # Ensure profile_id is included

            # Check if the education entry already exists
            existing_response = self.client.table("linkedin_educations").select("*").eq("profile_id", profile_id).eq("institution_id", education_data.institution_id).execute()

            if existing_response.data:
                # Entry exists, perform an update
                response = self.client.table("linkedin_educations").update(education_data_dict).eq("profile_id", profile_id).eq("institution_id", education_data.institution_id).execute()
                if response.data:
                    logger.info(f"Successfully updated education data for profile ID: {profile_id} for institution ID: {education_data.institution_id}")
                    return True
                else:
                    logger.error("Failed to update education data.")
                    return False
            else:
                # Entry does not exist, perform an insert
                response = self.client.table("linkedin_educations").insert(education_data_dict).execute()
                if response.data:
                    logger.info(f"Successfully inserted education data for profile ID: {profile_id} for institution ID: {education_data.institution_id}")
                    return True
                else:
                    logger.error("Failed to insert education data.")
                    return False

        except Exception as e:
            logger.error(f"Error inserting or updating LinkedIn education data: {str(e)}")
            return False

    async def upsert_linkedin_experience(self, profile_id: int, experience_data: LinkedInExperience) -> bool:
        """Insert or update LinkedIn experience data using profile_id and company_name."""
        try:
            # Prepare the data for insertion
            experience_data_dict = experience_data.to_dict()  # Assuming LinkedInExperience has a to_dict method
            experience_data_dict['profile_id'] = profile_id  # Ensure profile_id is included

            # Check if the experience entry already exists
            existing_response = self.client.table("linkedin_experiences").select("*").eq("profile_id", profile_id).eq("company_name", experience_data.company_name).execute()

            if existing_response.data:
                # Entry exists, perform an update
                response = self.client.table("linkedin_experiences").update(experience_data_dict).eq("profile_id", profile_id).eq("company_name", experience_data.company_name).execute()
                if response.data:
                    logger.info(f"Successfully updated experience data for profile ID: {profile_id} for company: {experience_data.company_name}")
                    return True
                else:
                    logger.error("Failed to update experience data.")
                    return False
            else:
                # Entry does not exist, perform an insert
                response = self.client.table("linkedin_experiences").insert(experience_data_dict).execute()
                if response.data:
                    logger.info(f"Successfully inserted experience data for profile ID: {profile_id} for company: {experience_data.company_name}")
                    return True
                else:
                    logger.error("Failed to insert experience data.")
                    return False

        except Exception as e:
            logger.error(f"Error inserting or updating LinkedIn experience data: {str(e)}")
            return False
