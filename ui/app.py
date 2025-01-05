import os
import sys

# Add the root project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import asyncio
from services.parser import ResumeParser
from services.db import ResumeDB
from models.schema import Resume

MAX_FILE_SIZE = 5 * 1024 * 1024

async def parse_and_display_resume(file_content: bytes, file_type: str):
    parser = ResumeParser()
    try:
        raw_text = await parser.extract_text(file_content, file_type)
        cleaned_text = "\n".join(line.strip() for line in raw_text.splitlines() if line.strip())
        
        st.subheader("Raw Resume Content")
        st.text_area("Content", cleaned_text, height=300)
        
        try:
            resume = await parser._parse_with_llm(cleaned_text)
            resume_id = await ResumeDB.save_resume(resume)
            resume.id = resume_id
            
            # Display Personal Information
            st.subheader("Personal Information")
            personal_info = resume.personal_information
            if personal_info:
                cols = st.columns(2)
                with cols[0]:
                    name = f"{personal_info.first_name} {personal_info.second_name}".strip()
                    st.write("**Name:**", name if name else "N/A")
                    st.write("**Email:**", personal_info.email if personal_info.email else "N/A")
                    st.write("**Phone:**", personal_info.phone_number if personal_info.phone_number else "N/A")
                with cols[1]:
                    st.write("**LinkedIn:**", personal_info.linkedin_url if personal_info.linkedin_url else "N/A")
                    st.write("**GitHub:**", personal_info.github_url if personal_info.github_url else "N/A")
                    st.write("**Website:**", personal_info.personal_website if personal_info.personal_website else "N/A")
            
            # Display Education
            st.subheader("Education")
            if resume.education:
                for idx, edu in enumerate(resume.education, 1):
                    st.markdown(f"**Education {idx}**")
                    cols = st.columns(2)
                    with cols[0]:
                        st.write("**Institution:**", edu.institution if edu.institution else "N/A")
                        st.write("**Degree:**", edu.degree if edu.degree else "N/A")
                        st.write("**Field:**", edu.field if edu.field else "N/A")
                        st.write("**GPA:**", edu.gpa if edu.gpa is not None else "N/A")
                    with cols[1]:
                        period = f"{edu.start_date} - {edu.end_date}" if edu.start_date or edu.end_date else "N/A"
                        st.write("**Period:**", period)
                        st.write("**Thesis:**", edu.master_thesis_title if edu.master_thesis_title else "N/A")
                        st.write("**Switch Major:**", "Yes" if edu.switch_major else "No")
                        st.write("**Graduated:**", "Yes" if edu.graduated_with_current_degree else "No")
            else:
                st.write("No education information found")
            
            # Display Experience
            st.subheader("Experience")
            if resume.employment:
                for idx, exp in enumerate(resume.employment, 1):
                    st.markdown(f"**Experience {idx}**")
                    cols = st.columns(2)
                    with cols[0]:
                        st.write("**Company Name:**", exp.company_name if exp.company_name else "N/A")
                        st.write("**Title:**", exp.job_title if exp.job_title else "N/A")
                        st.write("**Duration:**", exp.duration if exp.duration else "N/A")
                        st.write("**Leadership:**", exp.leadership if exp.leadership else "N/A")
                    with cols[1]:
                        st.write("**Company Website:**", exp.company_website if exp.company_website else "N/A")
                        st.write("**Period:**", f"{exp.start_date} - {exp.end_date}" if exp.start_date or exp.end_date else "N/A")
                    st.write("**Duty Description:**")
                    for duty in exp.duty_description:
                        st.write("-", duty if duty else "N/A")
                    st.write("**Tech Keywords:**", ", ".join(exp.tech_keywords) if exp.tech_keywords else "N/A")
                    st.write("**Reference:**", exp.reference if exp.reference else "N/A")
            else:
                st.write("No experience information found")
            
            # Display Internship
            st.subheader("Internship")
            if resume.internship:
                for idx, inter in enumerate(resume.internship, 1):
                    st.markdown(f"**Internship {idx}**")
                    cols = st.columns(2)
                    with cols[0]:
                        st.write("**Company Name:**", inter.company_name if inter.company_name else "N/A")
                        st.write("**Title:**", inter.job_title if inter.job_title else "N/A")
                        st.write("**Duration:**", inter.duration if inter.duration else "N/A")
                        st.write("**Leadership:**", inter.leadership if inter.leadership else "N/A")
                    with cols[1]:
                        st.write("**Company Website:**", inter.company_website if inter.company_website else "N/A")
                        st.write("**Period:**", f"{inter.start_date} - {inter.end_date}" if inter.start_date or inter.end_date else "N/A")
                        # Handle us_based_internship display
                        us_based = "N/A"
                        if hasattr(inter, 'us_based_internship') and inter.us_based_internship is not None:
                            us_based = "Yes" if inter.us_based_internship else "No"
                        st.write("**US Based Internship:**", us_based)
                    st.write("**Duty Description:**")
                    for duty in inter.duty_description:
                        st.write("-", duty if duty else "N/A")
                    st.write("**Tech Keywords:**", ", ".join(inter.tech_keywords) if inter.tech_keywords else "N/A")
                    st.write("**Reference:**", inter.reference if inter.reference else "N/A")
            else:
                st.write("No internship information found")
            
            # Display Project
            st.subheader("Project")
            if resume.project:
                for idx, proj in enumerate(resume.project, 1):
                    st.markdown(f"**Project {idx}**")
                    cols = st.columns(2)
                    with cols[0]:
                        st.write("**Title:**", proj.project_title if proj.project_title else "N/A")
                        st.write("**Teamwork or Independent:**", proj.teamwork_or_independent if proj.teamwork_or_independent else "N/A")
                        st.write("**Award or Credential:**", proj.award_or_credential if proj.award_or_credential else "N/A")
                    with cols[1]:
                        st.write("**Start Date:**", proj.start_date if proj.start_date else "N/A")
                        st.write("**End Date:**", proj.end_date if proj.end_date else "N/A")
                        st.write("**School Project:**", proj.school_project if proj.school_project else "N/A")
                    st.write("**Duty Description:**")
                    for duty in proj.project_description:
                        st.write("-", duty if duty else "N/A")
                    st.write("**Tech Keywords:**", ", ".join(proj.tech_keywords) if proj.tech_keywords else "N/A")
                    st.write("**Leadership:**", proj.leadership if proj.leadership else "N/A")
            else:
                st.write("No project information found")
            
            # Display Certificate
            st.subheader("Certificate")
            if resume.certificates:
                for idx, cert in enumerate(resume.certificates, 1):
                    st.markdown(f"**Certificate {idx}**")
                    st.write("**Name:**", cert.name if cert.name else "N/A")
                    st.write("**Source:**", cert.source if cert.source else "N/A")
                    st.write("**Receiving Time:**", cert.receiving_time if cert.receiving_time else "N/A")
            else:
                st.write("No certificate information found")
            
            # Display Honor and Award
            st.subheader("Honor and Award")
            if resume.honor_and_award:
                for idx, honor in enumerate(resume.honor_and_award, 1):
                    st.markdown(f"**Honor and Award {idx}**")
                    st.write("**Name:**", honor.name if honor.name else "N/A")
                    st.write("**Source:**", honor.source if honor.source else "N/A")
                    st.write("**Receiving Time:**", honor.receiving_time if honor.receiving_time else "N/A")
            else:
                st.write("No honor and award information found")
            
            # Display Academic Publication
            st.subheader("Academic Publication")
            if resume.academic_publication:
                for idx, pub in enumerate(resume.academic_publication, 1):
                    st.markdown(f"**Academic Publication {idx}**")
                    st.write("**Title:**", pub.title if pub.title else "N/A")
                    st.write("**Authors:**", pub.authors if pub.authors else "N/A")
                    st.write("**Journal of Publication:**", pub.journal_of_publication if pub.journal_of_publication else "N/A")
                    st.write("**Date of Publication:**", pub.date_of_publication if pub.date_of_publication else "N/A")
                    st.write("**Other Information:**", pub.other_information if pub.other_information else "N/A")
            else:
                st.write("No academic publication information found")
        
        except Exception as e:
            st.error(f"LLM Parsing failed: {str(e)}")
            st.info("Check the application logs for more details.")
    except Exception as e:
        st.error(f"File processing failed: {e}")

def main():
    st.title("Resume Parser")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
    if uploaded_file is not None:
        if uploaded_file.size > MAX_FILE_SIZE:
            st.error("File size exceeds the maximum limit of 5MB.")
            return
        file_type = uploaded_file.name.split('.')[-1].lower()
        file_content = uploaded_file.read()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(parse_and_display_resume(file_content, file_type))

if __name__ == "__main__":
    main()