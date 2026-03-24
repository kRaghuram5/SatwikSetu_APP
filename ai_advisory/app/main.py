"""
 AI Advisory Service (RAG) — Agent Chiguru AI
================================================
Consumes disease events, generates treatment advice via RAG, and serves advisories.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes.advisory import router as advisory_router
from app.kafka_consumer import start_consumer, stop_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """On startup: load knowledge base into Qdrant, then start Kafka consumer."""
    from app.rag.vectorstore import get_vectorstore
    get_vectorstore()   # eagerly ingest diseases.json → Qdrant on every cold start
    await start_consumer()
    yield
    await stop_consumer()


app = FastAPI(
    title=" AI Advisory Service (RAG)",
    description="LangChain-powered RAG pipeline for crop disease treatment advice",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(advisory_router)


@app.get("/health")
async def health():
    return {"service": "ai-advisory", "status": "healthy"}
