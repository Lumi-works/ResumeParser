import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import asyncio
from services.parser import ResumeParser
from services.db import ResumeDB

MAX_FILE_SIZE = 5 * 1024 * 1024

async def parse_and_display_resume(file_content: bytes, file_type: str):
    parser = ResumeParser()
    try:
        # Extract and clean text
        raw_text = parser._extract_text(file_content, file_type)
        cleaned_text = "\n".join(line.strip() for line in raw_text.splitlines() if line.strip())
        
        # Display raw content
        st.subheader("Raw Resume Content")
        st.text_area("Content", cleaned_text, height=300)
        
        try:
            # Parse with LLM
            resume = await parser._parse_with_llm(cleaned_text)
            
            # Save to database
            resume_id = await ResumeDB.save_resume(resume)
            resume.id = resume_id
            
            # Display parsed info
            st.subheader("Parsed Information")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Personal Info")
                st.write(f"Name: {resume.name}")
                st.write(f"Email: {resume.email}")
                
                st.write("### Education")
                for edu in resume.education:
                    st.markdown(f"""
                    **{edu.institution}**  
                    {edu.degree} in {edu.field}  
                    {edu.start_date} - {edu.end_date}
                    """)
            
            with col2:
                st.write("### Skills")
                for category, skills in resume.skills.items():
                    st.write(f"**{category.title()}:**")
                    st.write(", ".join(skills))
                
                st.write("### Experience")
                for exp in resume.experience:
                    st.markdown(f"""
                    **{exp.company}**  
                    *{exp.title}*  
                    {exp.location}  
                    {exp.start_date} - {exp.end_date}
                    """)
                    for highlight in exp.highlights:
                        st.markdown(f"- {highlight}")
                    st.markdown("---")
                    
        except Exception as e:
            st.error(f"LLM Parsing failed: {str(e)}")
            st.info("Check the raw content above for any formatting issues")
            
    except Exception as e:
        st.error(f"PDF extraction failed: {str(e)}")

def main():
    st.set_page_config(page_title="Resume Parser", layout="wide")
    st.title("Resume Parser")
    
    uploaded_file = st.file_uploader("Upload Resume", type=['pdf', 'doc', 'docx'])
    if uploaded_file:
        if uploaded_file.size > MAX_FILE_SIZE:
            st.error("File size exceeds 5MB limit")
            return
            
        file_type = uploaded_file.name.split('.')[-1].lower()
        file_content = uploaded_file.read()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(parse_and_display_resume(file_content, file_type))

if __name__ == "__main__":
    main()