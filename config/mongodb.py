import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize MongoDB connection
try:
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client.resume_parser
    resumes_collection = db.resumes
    
    # Test connection
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB")
    
except ServerSelectionTimeoutError as e:
    logger.error(f"Could not connect to MongoDB: {e}")
    # Initialize to None so imports don't fail
    client = None
    db = None
    resumes_collection = None
except Exception as e:
    logger.error(f"MongoDB initialization error: {e}")
    client = None
    db = None
    resumes_collection = None

# Export these variables
__all__ = ['client', 'db', 'resumes_collection']