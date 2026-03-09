FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main/sgw.py ./sgw.py
COPY main/ingestion.py ./ingestion.py

EXPOSE 8000

CMD ["uvicorn", "sgw:app", "--host", "0.0.0.0", "--port", "8000"]