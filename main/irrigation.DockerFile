FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main/irrigation.py ./irrigation.py
COPY main/processor.py ./processor.py
COPY main/ingestion.py ./ingestion.py



CMD ["python","processor.py"]