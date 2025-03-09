FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV TIMEOUT=300

EXPOSE 8080

# Use uvicorn directly with increased timeout
CMD uvicorn main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive $TIMEOUT