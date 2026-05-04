# Weather Service Dockerfile
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements if present
COPY weather/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy weather service code
COPY weather /app/weather
COPY shared /app/shared

# Expose port
EXPOSE 8006

# Start FastAPI app
CMD ["uvicorn", "weather.app.main:app", "--host", "0.0.0.0", "--port", "8006"]
