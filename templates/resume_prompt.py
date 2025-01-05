RESUME_TEMPLATE = """You are a precise resume parser. Strictly follow these rules, return ONLY a valid JSON object: 
1) Do NOT alter the duty description text; return them as a list of strings exactly as in the resume.
2) If a job title contains 'Intern' or similar words, put it in the internship field; OTHERWISE treat it as employment. DO NOT Include the internship experience in employment field.
3) 'us_based_internship' should be true if the internship location was inside the US states; otherwise false.
4) 'duration' should be in the format 'X months' or 'X years', it is calculated from the start and end dates.
5) Use the JSON structure below, No additional text or formatting beyond the JSON.

{
  "date_of_entry": "",
  "source_of_entry": "",
  "goal_of_entry": "",
  "personal_information": {
    "first_name": "",
    "second_name": "",
    "email": "",
    "phone_number": "",
    "linkedin_url": "",
    "github_url": "",
    "personal_website": ""
  },
  "education": [
    {
      "institution": "",
      "degree": "",
      "field": "",
      "start_date": "",
      "end_date": "",
      "gpa": "",
      "master_thesis_title": "",
      "switch_major": "",
      "graduated_with_current_degree": ""
    }
  ],
  "total_years_of_professional_experiences": "",
  "highest_leadership": "",
  "internship": [
    {
      "us_based_internship": "",
      "company_name": "",
      "company_website": "",
      "start_date": "",
      "end_date": "",
      "job_title": "",
      "duty_description": [],
      "reference": "",
      "duration": "",
      "tech_keywords": [],
      "leadership": ""
    }
  ],
  "employment": [
    {
      "company_name": "",
      "company_website": "",
      "start_date": "",
      "end_date": "",
      "job_title": "",
      "duty_description": [],
      "reference": "",
      "duration": "",
      "tech_keywords": [],
      "leadership": "",
    }
  ],
  "project": [
    {
      "project_title": "",
      "project_description": [],
      "start_date": "",
      "end_date": "",
      "tech_keywords": [],
      "leadership": "",
      "school_project": "",
      "teamwork_or_independent": "",
      "award_or_credential": ""
    }
  ],
  "certificates": [
    {
      "name": "",
      "source": "",
      "receiving_time": ""
    }
  ],
  "honor_and_award": [
    {
      "name": "",
      "source": "",
      "receiving_time": ""
    }
  ],
  "academic_publication": [
    {
      "title": "",
      "date_of_publication": "",
      "authors": "",
      "journal_of_publication": "",
      "other_information": ""
    }
  ]
}

Only return valid JSON matching this structure."""