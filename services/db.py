import logging
import os
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from models.schema import Resume

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class ResumeDB:
    def __init__(self):
        uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGODB_DB', 'resume_parser')
        collection_name = os.getenv('MONGODB_COLLECTION', 'resumes')
        
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
        # Create compound index for name and email fields
        self.collection.create_index(
            [
                ("personal_information.first_name", 1),
                ("personal_information.second_name", 1),
                ("personal_information.email", 1)
            ],
            unique=True,
            partialFilterExpression={
                "personal_information.first_name": {"$exists": True},
                "personal_information.second_name": {"$exists": True},
                "personal_information.email": {"$exists": True}
            }
        )
        
        logger.info("Successfully connected to MongoDB")
    
    @staticmethod
    def serialize_resume(resume: Resume) -> dict:
        # Convert Pydantic model to dict, handling optional fields
        return resume.dict(exclude_unset=True)
    
    @classmethod
    async def save_resume(cls, resume: Resume) -> str:
        try:
            # Initialize the database connection
            db_instance = cls()
            resume_data = cls.serialize_resume(resume)
            
            # Ensure 'employment' field exists and is a list
            if 'employment' not in resume_data or resume_data['employment'] is None:
                resume_data['employment'] = []
            
            # Similarly handle other list fields if necessary
            # For example:
            # if 'education' not in resume_data or resume_data['education'] is None:
            #     resume_data['education'] = []
            
            # Remove null or empty email from the document
            if resume_data.get('email') is None:
                resume_data.pop('email', None)
            
            # Extract personal information
            personal_info = resume_data.get('personal_information', {})
            first_name = personal_info.get('first_name')
            second_name = personal_info.get('second_name')
            email = personal_info.get('email')

            if first_name and second_name and email:
                # Update existing or insert new based on composite key
                result = db_instance.collection.find_one_and_replace(
                    {
                        "personal_information.first_name": first_name,
                        "personal_information.second_name": second_name,
                        "personal_information.email": email
                    },
                    resume_data,
                    upsert=True,
                    return_document=ReturnDocument.AFTER
                )
                return str(result["_id"])
            else:
                # If any key field is missing, create new document
                result = db_instance.collection.insert_one(resume_data)
                return str(result.inserted_id)

        except PyMongoError as e:
            logger.error(f"Failed to save resume: {e}")
            raise
        except KeyError as e:
            logger.error(f"Missing key during save: {e}")
            raise