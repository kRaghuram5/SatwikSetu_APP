"""
 Irrigation Recommendation Service — Agent Chiguru AI
========================================================
Rule-based irrigation scheduling with Redis caching.
"""

from fastapi import FastAPI
from app.routes.recommend import router as recommend_router

app = FastAPI(
    title=" Irrigation Recommendation Service",
    description="Rule-based irrigation scheduling based on crop, soil, and weather",
    version="1.0.0",
)

app.include_router(recommend_router)


@app.get("/health")
async def health():
    return {"service": "irrigation", "status": "healthy"}
