# filepath: /Users/lumixu/Desktop/ResumeParser/Dockerfile

# 1. Use a lightweight base image
FROM python:3.9-slim

# 2. Create a working directory
WORKDIR /app

# 3. Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy source code
COPY . .

# 5. Expose Streamlit default port
EXPOSE 8501

# 6. Entry point to run the app
CMD ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]