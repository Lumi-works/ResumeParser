from config.mongodb import resumes_collection
from models.schema import Resume
import logging
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)

class ResumeDB:
    @staticmethod
    async def save_resume(resume: Resume) -> str:
        try:
            resume_dict = resume.dict()
            
            # Try to update existing resume or insert new one
            result = resumes_collection.find_one_and_replace(
                {"email": resume_dict["email"]},
                resume_dict,
                upsert=True,
                return_document=True
            )
            
            logger.info(f"Resume saved with ID: {result['_id']}")
            return str(result['_id'])
            
        except Exception as e:
            logger.error(f"Failed to save resume: {str(e)}")
            raise

    @staticmethod
    async def get_resume(resume_id: str) -> Resume:
        doc = resumes_collection.find_one({"_id": ObjectId(resume_id)})
        return Resume.parse_obj(doc) if doc else None