from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator

class PersonalInformation(BaseModel):
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    personal_website: Optional[str] = None

class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[Union[str, float]] = None  # Allow GPA to be string or float
    master_thesis_title: Optional[str] = None
    switch_major: Optional[bool] = False
    graduated_with_current_degree: Optional[bool] = False

    @validator("gpa", pre=True)
    def parse_gpa(cls, v):
        # If it's an empty string or None, return None
        if not v:
            return None
        # If the string has a '/', parse only the first part
        if isinstance(v, str) and "/" in v:
            num, _ = v.split("/")
            try:
                return float(num.strip())
            except ValueError:
                return None
        # Otherwise, try converting to float
        try:
            return float(v)
        except ValueError:
            return None
    
    @validator('switch_major', 'graduated_with_current_degree', pre=True)
    def parse_bool(cls, value):
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes']
        return bool(value)

class Employment(BaseModel):
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    job_title: Optional[str] = None
    duty_description: Optional[List[str]] = Field(default_factory=list)
    reference: Optional[str] = None
    duration: Optional[str] = None
    tech_keywords: Optional[List[str]] = Field(default_factory=list)
    leadership: Optional[str] = None

class Internship(BaseModel):
    us_based_internship: Optional[bool] = False
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    job_title: Optional[str] = None
    duty_description: Optional[List[str]] = Field(default_factory=list)
    reference: Optional[str] = None
    duration: Optional[str] = None
    tech_keywords: Optional[List[str]] = Field(default_factory=list)
    leadership: Optional[str] = None

class Project(BaseModel):
    project_title: Optional[str] = None
    project_description: Optional[List[str]] = Field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    tech_keywords: Optional[List[str]] = Field(default_factory=list)
    leadership: Optional[str] = None
    school_project: Optional[str] = None
    teamwork_or_independent: Optional[str] = None
    award_or_credential: Optional[str] = None

class Certificate(BaseModel):
    name: Optional[str] = None
    source: Optional[str] = None
    receiving_time: Optional[str] = None

class HonorAndAward(BaseModel):
    name: Optional[str] = None
    source: Optional[str] = None
    receiving_time: Optional[str] = None

class AcademicPublication(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    journal_of_publication: Optional[str] = None
    date_of_publication: Optional[str] = None
    other_information: Optional[str] = None

class Resume(BaseModel):
    id: Optional[str] = None
    date_of_entry: Optional[str] = None
    source_of_entry: Optional[str] = None
    goal_of_entry: Optional[str] = None
    personal_information: Optional[PersonalInformation] = None
    education: Optional[List[Education]] = Field(default_factory=list)
    employment: Optional[List[Employment]] = Field(default_factory=list)
    internship: Optional[List[Internship]] = Field(default_factory=list)
    project: Optional[List[Project]] = Field(default_factory=list)
    certificates: Optional[List[Certificate]] = Field(default_factory=list)
    honor_and_award: Optional[List[HonorAndAward]] = Field(default_factory=list)
    academic_publication: Optional[List[AcademicPublication]] = Field(default_factory=list)
    total_years_of_professional_experiences: Optional[str] = None
    highest_leadership: Optional[str] = None