"""Irrigation recommendation endpoint."""

import json
import redis
import logging
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from shared.database import get_db
from shared.services.weather_service import get_weather_service
from app.engine.rules import get_irrigation_recommendation, get_weather_adjusted_irrigation
from app.config import get_irrigation_settings

router = APIRouter()
settings = get_irrigation_settings()
logger = logging.getLogger(__name__)

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


@router.get("/irrigation-with-weather")
def recommend_irrigation_with_weather(
    farm_id: str = Query(..., description="Farm identifier"),
    crop: str = Query(..., description="Crop type (e.g., rice, wheat, tomato)"),
    latitude: float = Query(..., description="Farm latitude"),
    longitude: float = Query(..., description="Farm longitude"),
    soil_moisture: float = Query(None, description="Current soil moisture percentage"),
    temperature: float = Query(None, description="Current temperature in °C"),
    growth_stage: str = Query(None, description="Growth stage (e.g., vegetative, flowering)"),
    db: Session = Depends(get_db),
    weather_service=Depends(get_weather_service),
):
    """
    Get irrigation recommendation enhanced with real-time weather data and forecast.
    
    Combines:
    - Rule-based irrigation engine
    - Current soil conditions
    - Real-time weather data
    - 5-day weather forecast
    - Rainfall prediction
    
    Returns:
        Enhanced irrigation plan with weather-adjusted recommendations
    """
    try:
        # Get base irrigation recommendation
        base_recommendation = get_irrigation_recommendation(
            crop=crop,
            soil_moisture=soil_moisture,
            temperature=temperature,
            growth_stage=growth_stage,
        )
        
        # Get real-time weather
        current_weather = weather_service.get_current_weather(latitude, longitude)
        
        # Get weather forecast
        forecast = weather_service.get_weather_forecast(latitude, longitude, days=5)
        
        # Get agricultural advisory
        advisory = weather_service.get_agricultural_advisory(latitude, longitude, crop)
        
        # Adjust irrigation based on weather
        enhanced_recommendation = get_weather_adjusted_irrigation(
            base_recommendation=base_recommendation,
            current_weather=current_weather,
            forecast=forecast,
            crop=crop,
            growth_stage=growth_stage or "vegetative"
        )
        
        # Combine all information
        result = {
            "farm_id": farm_id,
            "crop": crop,
            "generated_at": current_weather["timestamp"],
            "base_irrigation": base_recommendation,
            "enhanced_irrigation": enhanced_recommendation,
            "current_weather": {
                "temperature": current_weather["temperature"],
                "humidity": current_weather["humidity"],
                "rainfall_today_mm": current_weather["rainfall_mm"],
                "wind_speed_kmh": current_weather["wind_speed"],
                "condition": current_weather["condition"],
            },
            "weather_forecast_5days": forecast["forecast"][:5],
            "agricultural_advisory": advisory["recommendations"],
            "alerts": advisory.get("alerts", []),
            "irrigation_adjustments": enhanced_recommendation.get("adjustments", []),
        }
        
        logger.info(f"Generated enhanced irrigation for farm {farm_id}, crop {crop}")
        
        return {
            "status": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"Error generating enhanced irrigation recommendation: {e}")
        # Fall back to base recommendation
        base_recommendation = get_irrigation_recommendation(
            crop=crop,
            soil_moisture=soil_moisture,
            temperature=temperature,
            growth_stage=growth_stage,
        )
        return {
            "status": "success_with_fallback",
            "warning": "Could not integrate weather data, returning base recommendation",
            "data": base_recommendation
        }

