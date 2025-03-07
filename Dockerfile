# Use Python 3.10 slim image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV TIMEOUT=300

# Expose the port
EXPOSE 8080

# Use gunicorn as the production server
RUN pip install gunicorn

# Start the application with gunicorn
CMD exec gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind :$PORT --timeout 300 --access-logfile - --error-logfile -


