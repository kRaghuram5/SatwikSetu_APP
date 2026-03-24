FROM python:3.11-slim

WORKDIR /app

COPY market_price/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY market_price/app ./app
COPY shared ./shared

EXPOSE 8004

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
