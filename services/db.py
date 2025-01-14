import logging
import os
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from models.schema import Resume, User

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class ResumeDB:
    def __init__(self):
        uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = 'resume_parser_db'
        
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.resumes_collection = self.db['resumes']
        self.users_collection = self.db['users']
        
        # Create compound index for resuming uniqueness
        self.resumes_collection.create_index(
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
        
        # Create index for users' emails
        self.users_collection.create_index("email", unique=True)
        
        logger.info("Successfully connected to MongoDB")
    
    @staticmethod
    def serialize_resume(resume: Resume) -> dict:
        return resume.dict(exclude_unset=True)
    
    @classmethod
    async def save_resume(cls, resume: Resume) -> str:
        try:
            db_instance = cls()
            resume_data = cls.serialize_resume(resume)
            
            if 'employment' not in resume_data or resume_data['employment'] is None:
                resume_data['employment'] = []
            
            if resume_data.get('email') is None:
                resume_data.pop('email', None)
            
            personal_info = resume_data.get('personal_information', {})
            first_name = personal_info.get('first_name')
            second_name = personal_info.get('second_name')
            email = personal_info.get('email')

            if first_name and second_name and email:
                result = db_instance.resumes_collection.find_one_and_replace(
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
                result = db_instance.resumes_collection.insert_one(resume_data)
                return str(result.inserted_id)

        except PyMongoError as e:
            logger.error(f"Failed to save resume: {e}")
            raise
        except KeyError as e:
            logger.error(f"Missing key during save: {e}")
            raise

    def create_user(self, user: User):
        try:
            self.users_collection.insert_one(user.dict())
            logger.info("User created successfully")
        except PyMongoError as e:
            logger.error(f"Failed to create user: {e}")
            raise

    def get_user(self, email: str):
        try:
            return self.users_collection.find_one({"email": email})
        except PyMongoError as e:
            logger.error(f"Failed to retrieve user: {e}")
            raise