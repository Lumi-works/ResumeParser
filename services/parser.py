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
        self.doc_parser = None  # Removed as parsing is handled by static methods
    
    async def _parse_with_llm(self, text: str) -> Resume:
        try:
            messages = self.prompt.format_messages(text=text)
            response = await self.llm.ainvoke(messages)

            # Clean and validate response
            cleaned_response = response.content.strip()
            logger.debug(f"Cleaned Response: {cleaned_response[:500]}")  # Log first 500 chars

            if not cleaned_response.startswith("{"):
                raise ValueError(f"Invalid JSON format: {cleaned_response[:50]}")

            # Parse JSON
            parsed_data = json.loads(cleaned_response)
            logger.debug(f"Parsed JSON: {parsed_data}")  # Log the full parsed JSON

            # Validate and convert to Resume model
            try:
                resume = Resume(**parsed_data)
                logger.debug("Resume parsed successfully.")
            except ValidationError as e:
                logger.error(f"Pydantic Validation Error: {e.json()}")  # Log detailed validation errors
                raise ValueError(f"Pydantic Validation Error: {e.json()}")

            return resume

        except Exception as e:
            logger.error(f"LLM Parsing failed: {str(e)}")
            raise

    async def extract_text(self, file_content: bytes, file_type: str) -> str:
        try:
            if file_type == 'docx':
                return self.parse_docx(file_content)
            elif file_type == 'pdf':
                return self.parse_pdf(file_content)
            else:
                raise ValueError("Unsupported file type")
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise ValueError("Text extraction failed") from e

    async def process_resume(self, file_content: bytes) -> Resume:
        try:
            text = await self.extract_text(file_content)
            resume = await self._parse_with_llm(text)
            resume_id = await ResumeDB.save_resume(resume)
            resume.id = resume_id
            return resume
            
        except Exception as e:
            logger.error(f"Failed to process resume: {str(e)}")
            raise



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
