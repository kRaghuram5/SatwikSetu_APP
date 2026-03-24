FROM python:3.11-slim

WORKDIR /app

COPY notification/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY notification/app ./app
COPY shared ./shared

EXPOSE 8005

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
