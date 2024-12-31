from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict
from datetime import date, datetime

class Education(BaseModel):
    institution: str
    degree: str
    field: str
    start_date: str
    end_date: str
    gpa: Optional[float] = None

    @validator("gpa", pre=True)
    def parse_gpa(cls, v):
        # If it's an empty string or None, return None
        if not v:
            return None
        # If the string has a '/', parse only the first part
        if isinstance(v, str) and "/" in v:
            num, _ = v.split("/")
            return float(num.strip())
        # Otherwise, try converting to float
        try:
            return float(v)
        except ValueError:
            return None

class Experience(BaseModel):
    company: str
    title: str
    location: str = ''
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    highlights: List[str] = []

class Project(BaseModel):
    name: str
    description: str
    technologies: List[str]
    url: Optional[str] = None
    highlights: List[str]

class Award(BaseModel):
    title: str
    issuer: str
    date: Optional[date]
    description: Optional[str]

class Resume(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    skills: Dict[str, List[str]] = Field(default_factory=dict)
    awards: List[Award] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)