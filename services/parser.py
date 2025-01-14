import json
import logging
from io import BytesIO
from docx import Document
from pydantic import ValidationError
from models.schema import Resume
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from PyPDF2 import PdfReader
from templates.resume_prompt import RESUME_TEMPLATE
from datetime import datetime
import dateparser

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ResumeParser:
    @staticmethod
    def parse_docx(file_content: bytes) -> str:
        doc = Document(BytesIO(file_content))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    
    @staticmethod
    def parse_pdf(file_content: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(file_content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text
        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            raise ValueError("Text extraction failed: 'parse_pdf' method encountered an error.")
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, max_tokens=2000)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    RESUME_TEMPLATE
                ),
                (
                    "user",
                    "Parse this resume into a clean JSON object. Include every detail. Text:\n{{ text }}"
                ),
            ],
            template_format="jinja2",
        )
    
    @staticmethod
    def parse_date(date_str: str) -> str:
        if not date_str or date_str.lower() == 'present':
            return datetime.now().strftime('%Y-%m-%d')
        
        parsed_date = dateparser.parse(date_str)
        if parsed_date:
            return parsed_date.strftime('%Y-%m-%d')
        raise ValueError(f"Could not parse date: {date_str}")

    def preprocess_dates(self, data: dict) -> dict:
        if 'employment' in data:
            for job in data['employment']:
                if 'start_date' in job:
                    job['start_date'] = self.parse_date(job['start_date'])
                if 'end_date' in job:
                    job['end_date'] = self.parse_date(job['end_date'])
        return data

    async def parse(self, file_content: bytes, file_type: str, username: str) -> dict:
        try:
            # Extract text based on file type
            if file_type == "application/pdf":
                text = self.parse_pdf(file_content)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = self.parse_docx(file_content)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            # Parse with LLM
            messages = self.prompt.format_messages(text=text)
            response = await self.llm.ainvoke(messages)
            cleaned_response = response.content.strip()

            # Parse JSON response
            parsed_data = json.loads(cleaned_response)
            
            # Process dates
            parsed_data = self.preprocess_dates(parsed_data)
            
            # Add metadata
            parsed_data.update({
                "username": username,
                "resume_content": text,
                "file_type": file_type
            })

            # Validate with Resume model
            Resume(**parsed_data)
            return parsed_data

        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise ValueError(f"Invalid resume format: {str(e)}")
        except Exception as e:
            logger.error(f"Parse error: {e}")
            raise ValueError(f"Failed to parse resume: {str(e)}")

def build_education_list(education_data):
    """Ensures each item is turned into an Education object exactly once."""
    result = []
    for edu_item in education_data:
        if isinstance(edu_item, Education):
            # Already an Education model instance
            result.append(edu_item)
        elif isinstance(edu_item, dict):
            # Ensure all required fields are present
            edu_item.setdefault("degree", "Unknown")
            edu_item.setdefault("field", "Unknown")
            result.append(Education(**edu_item))
        else:
            raise ValueError("Education data must be a dict or Education instance.")
    return result