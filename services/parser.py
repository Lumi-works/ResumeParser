import logging
import json
import PyPDF2
from docx import Document
from io import BytesIO
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from models.schema import Resume, Education, Experience
from uuid import uuid4
from services.db import ResumeDB
from pydantic import BaseModel, validator
from typing import Optional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DocumentParser:
    @staticmethod
    def parse_pdf(file_content: bytes) -> str:
        pdf = PyPDF2.PdfReader(BytesIO(file_content))
        return "\n".join(page.extract_text() for page in pdf.pages)
    
    @staticmethod
    def parse_docx(file_content: bytes) -> str:
        doc = Document(BytesIO(file_content))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

class ResumeParser:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, max_tokens=2000)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a precise resume parser. Return ONLY a valid JSON object. 
Include all bullet points and experiences without truncation, preserving detail. 
No additional text or formatting beyond the JSON. 
Example JSON structure:
{
    "name": "candidate name",
    "email": "email",
    "education": [{
        "institution": "university name",
        "degree": "degree type",
        "field": "field of study",
        "start_date": "start date",
        "end_date": "end date",
        "gpa": "gpa if available"
    }],
    "experience": [{
        "company": "company name",
        "title": "job title",
        "location": "location",
        "start_date": "start date",
        "end_date": "end date",
        "highlights": ["bullet points"]
    }],
    "skills": {
        "technical": ["skills"],
        "tools": ["tools"],
        "languages": ["languages"]
    }
}"""
                ),
                (
                    "user",
                    "Parse this resume into a clean JSON object. Include every detail. Text:\n{{ text }}"
                ),
            ],
            template_format="jinja2",
        )
        self.doc_parser = DocumentParser()

    async def _parse_with_llm(self, text: str) -> Resume:
        try:
            messages = self.prompt.format_messages(text=text)
            response = await self.llm.ainvoke(messages)

            # Clean and validate response
            cleaned_response = response.content.strip()
            if not cleaned_response.startswith("{"):
                raise ValueError(f"Invalid JSON format: {cleaned_response[:50]}")

            # Parse JSON
            parsed_data = json.loads(cleaned_response)
            logger.debug(f"Parsed JSON: {parsed_data}")

            # Convert education entries once
            parsed_education = build_education_list(parsed_data.get("education", []))

            resume = Resume(
                id=str(uuid4()),
                name=parsed_data.get("name", "Unknown"),
                email=parsed_data.get("email", "no-email@example.com"),
                education=parsed_education,
                experience=[Experience(**exp) for exp in parsed_data.get("experience", [])],
                skills=parsed_data.get("skills", {}),
                projects=parsed_data.get("projects", []),
                awards=[],
                metadata={},
            )

            return resume

        except json.JSONDecodeError as je:
            logger.error(f"JSON parsing failed: {je}")
            logger.error(f"Raw response: {response.content}")
            raise ValueError(f"Invalid JSON from LLM: {je}")
        except Exception as e:
            logger.error(f"LLM parsing error: {str(e)}")
            raise

    def _extract_text(self, file_content: bytes, file_type: str) -> str:
        try:
            if file_type == 'pdf':
                return self.doc_parser.parse_pdf(file_content)
            elif file_type in ['doc', 'docx']:
                return self.doc_parser.parse_docx(file_content)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            raise ValueError(f"Text extraction failed: {str(e)}")

    async def process_resume(self, file_content: bytes) -> Resume:
        try:
            text = self._extract_text(file_content)
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
