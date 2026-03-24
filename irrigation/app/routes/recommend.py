"""Irrigation recommendation endpoint."""

import json
import redis
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from shared.database import get_db
from app.engine.rules import get_irrigation_recommendation
from app.config import get_irrigation_settings

router = APIRouter()
settings = get_irrigation_settings()

# Redis client for caching
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception:
    redis_client = None


@router.get("/irrigation")
def recommend_irrigation(
    crop: str = Query(..., description="Crop type (e.g., rice, wheat, tomato)"),
    soil_moisture: float = Query(None, description="Current soil moisture percentage"),
    temperature: float = Query(None, description="Current temperature in °C"),
    growth_stage: str = Query(None, description="Growth stage (e.g., vegetative, flowering)"),
    db: Session = Depends(get_db),
):
    """
    Get irrigation recommendation based on crop, conditions, and growth stage.
    Results are cached in Redis for 1 hour.
    """
    # Check cache
    cache_key = f"irrigation:{crop}:{growth_stage}:{soil_moisture}:{temperature}"
    if redis_client:
        try:
            cached = redis_client.get(cache_key)
            if cached:
                result = json.loads(cached)
                result["cached"] = True
                return result
        except Exception:
            pass

    # Generate recommendation
    result = get_irrigation_recommendation(
        crop=crop,
        soil_moisture=soil_moisture,
        temperature=temperature,
        growth_stage=growth_stage,
    )

    # Cache result
    if redis_client:
        try:
            redis_client.setex(cache_key, 3600, json.dumps(result))  # 1 hour TTL
        except Exception:
            pass

    result["cached"] = False
    return result
