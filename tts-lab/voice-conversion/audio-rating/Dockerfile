# Use the official Streamlit base image
FROM python:3.9-slim

# Install git in the container
RUN apt-get update && apt-get install -y git

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the Streamlit app files into the container
COPY app.py /app/main.py

# Copy the environment file into the container
COPY .env /app/.env

# Expose the Streamlit port
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port", "8501"]
