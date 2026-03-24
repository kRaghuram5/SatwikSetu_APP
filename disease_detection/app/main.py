"""
 Disease Detection Service — Agent Chiguru AI
================================================
Accepts crop images, runs inference, and publishes detection events.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes.detect import router as detect_router
from app.kafka_producer import get_kafka_producer, close_kafka_producer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start Kafka producer on startup, close on shutdown."""
    await get_kafka_producer()
    yield
    await close_kafka_producer()


app = FastAPI(
    title=" Disease Detection Service",
    description="Crop disease detection via image classification",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(detect_router)


@app.get("/health")
async def health():
    return {"service": "disease-detection", "status": "healthy"}
