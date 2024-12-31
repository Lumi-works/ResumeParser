import os
import sys
import pytest
from unittest.mock import Mock, patch
import asyncio

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock MongoDB
mock_db = Mock()
mock_db.save_resume = Mock(return_value="test_id")

@pytest.mark.asyncio
@patch('services.db.ResumeDB.save_resume')
async def test_parser(mock_save):
    from services.parser import ResumeParser
    
    # Configure mock
    mock_save.return_value = "test_id"
    
    parser = ResumeParser()
    
    # Sample text that the LLM should convert to JSON
    # In a live scenario, you may want to mock the LLM call instead of hitting the real API
    test_text = """
    Name: Jane Roe
    Email: jane.roe@example.com
    Education:
      - institution: University of Testing
        degree: Bachelor of Science
        field: Computer Science
        start_date: 2020
        end_date: 2024
        gpa: 3.8
    Experience:
      - company: Acme Corp
        title: Software Engineer
        location: Remote
        start_date: 2022
        end_date: Present
        highlights: ["Developed new features", "Improved code coverage"]
    """
    
    resume = await parser._parse_with_llm(test_text)
    
    # Basic assertions
    assert resume.name == "Jane Roe"
    assert resume.email == "jane.roe@example.com"
    assert len(resume.education) == 1
    edu = resume.education[0]
    assert edu.institution == "University of Testing"
    assert edu.gpa == 3.8

    assert len(resume.experience) == 1
    exp = resume.experience[0]
    assert exp.company == "Acme Corp"
    assert "Developed new features" in exp.highlights