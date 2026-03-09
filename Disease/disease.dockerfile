FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Disease/Disease.py ./Disease.py
COPY Disease/processor.py ./processor.py
COPY Disease/ingestion.py ./ingestion.py

CMD ["python", "processor.py"]
