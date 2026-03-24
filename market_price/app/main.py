"""
 Market Price Service — Agent Chiguru AI
===========================================
Mandi price data with Redis caching and trend analysis.
"""

from fastapi import FastAPI
from app.routes.prices import router as prices_router

app = FastAPI(
    title=" Market Price Service",
    description="Real-time mandi market prices for crops across India",
    version="1.0.0",
)

app.include_router(prices_router)


@app.get("/health")
async def health():
    return {"service": "market-price", "status": "healthy"}
