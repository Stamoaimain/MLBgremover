FROM python:3.10-slim

WORKDIR /app

# Install system dependencies more efficiently
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
# Increase timeouts and memory management
ENV GUNICORN_CMD_ARGS="--timeout 600 --keep-alive 120 --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind :$PORT --log-level info"

EXPOSE 8080

# Use gunicorn with longer timeouts
CMD exec gunicorn main:app $GUNICORN_CMD_ARGS