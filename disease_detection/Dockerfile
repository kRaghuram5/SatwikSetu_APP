FROM python:3.11-slim

WORKDIR /app

COPY disease_detection/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY disease_detection/app ./app
COPY shared ./shared

RUN mkdir -p /app/uploads /app/model

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
