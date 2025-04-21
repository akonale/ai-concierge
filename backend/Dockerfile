# backend/Dockerfile

# Use an official Python runtime as a parent image (updated to 3.11.11)
# Using slim-bookworm for a smaller image size with Python 3.11
FROM python:3.11.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1 # Prevents python from writing .pyc files
ENV PYTHONUNBUFFERED 1      # Ensures logs are sent straight to terminal without buffering
ENV PORT 5000               # Define the port the application will run on

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed (e.g., for certain Python packages)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip
# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .
# Install dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the working directory
# This includes your main.py, app/ directory, etc.
COPY . .

# Expose the port the app runs on
# This should match the $PORT environment variable and the uvicorn command --port
EXPOSE 5000

# Define the command to run the application
# Runs Uvicorn which serves the FastAPI app defined in main.py as 'app'
# Binds to 0.0.0.0 to be accessible from outside the container
# Uses the $PORT environment variable defined above
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]

# Note: For development with hot-reloading, the command might be overridden
# in docker-compose.yml to include --reload, but this CMD is suitable for production.
