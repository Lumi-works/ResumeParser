import sys
import os
import streamlit as st
import asyncio
from services.parser import ResumeParser
from services.db import ResumeDB
from models.schema import Resume, User
import bcrypt

# Initialize session state and database
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

db = ResumeDB()
resumes_collection = db.resumes_collection
users_collection = db.users_collection

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def login_page():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            user = users_collection.find_one({"email": email})
            if user and check_password(password, user['password']):
                st.session_state['username'] = email
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    with col2:
        if st.button("Sign Up"):
            st.session_state['page'] = 'signup'
            st.rerun()

def signup_page():
    st.title("Sign Up")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create Account"):
            if password != confirm_password:
                st.error("Passwords do not match")
            elif users_collection.find_one({"email": email}):
                st.error("Email already exists")
            else:
                hashed_pw = hash_password(password)
                users_collection.insert_one({
                    "email": email,
                    "password": hashed_pw
                })
                st.success("Account created successfully!")
                st.session_state['page'] = 'login'
    with col2:
        if st.button("Back to Login"):
            st.session_state['page'] = 'login'

async def parse_and_display_resume(file_content: bytes, file_type: str, username: str):
    parser = ResumeParser()
    try:
        parsed_data = await parser.parse(file_content, file_type, username)
        resume = Resume(**parsed_data)
        resume_id = await db.save_resume(resume)
        
        st.subheader("Parsed Resume Data")
        st.json(parsed_data)
        st.success(f"Resume saved with ID: {resume_id}")
        
    except Exception as e:
        st.error(f"Error parsing resume: {str(e)}")

def main():
    if st.session_state['username']:
        st.sidebar.write(f"Logged in as {st.session_state['username']}")
        if st.sidebar.button("Logout"):
            st.session_state['username'] = None
            st.session_state['page'] = 'login'
            st.rerun()

        st.title("Resume Parser")
        
        uploaded_file = st.file_uploader("Choose a resume...", type=["pdf", "docx"])
        if uploaded_file:
            file_content = uploaded_file.read()
            file_type = uploaded_file.type
            asyncio.run(parse_and_display_resume(
                file_content, 
                file_type, 
                st.session_state['username']
            ))

        # View Parsed Resumes
        st.subheader("Your Parsed Resumes")
        user_resumes = resumes_collection.find({"username": st.session_state['username']})
        for resume in user_resumes:
            st.write(resume)
    else:
        if st.session_state['page'] == "login":
            login_page()
        elif st.session_state['page'] == "signup":
            signup_page()

if __name__ == "__main__":
    main()