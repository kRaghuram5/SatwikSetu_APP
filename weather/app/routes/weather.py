"""Weather API endpoints."""

from fastapi import APIRouter, Query, Depends, HTTPException
from shared.services.weather_service import get_weather_service, WeatherService
import logging

router = APIRouter(prefix="/api/v1/weather", tags=["weather"])
logger = logging.getLogger(__name__)


@router.get("/current")
def get_current_weather(
    latitude: float = Query(..., description="Farm latitude"),
    longitude: float = Query(..., description="Farm longitude"),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get current weather conditions at farm location.
    
    Returns:
        Current weather data including temperature, humidity, rainfall, wind
    """
    try:
        weather = weather_service.get_current_weather(latitude, longitude)
        return {"status": "success", "data": weather}
    except Exception as e:
        logger.error(f"Error getting current weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast")
def get_weather_forecast(
    latitude: float = Query(..., description="Farm latitude"),
    longitude: float = Query(..., description="Farm longitude"),
    days: int = Query(5, ge=1, le=7, description="Number of days to forecast"),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get 5-7 day weather forecast.
    
    Returns:
        Aggregated daily forecast with temperature, rainfall, wind, conditions
    """
    try:
        forecast = weather_service.get_weather_forecast(latitude, longitude, days)
        return {"status": "success", "data": forecast}
    except Exception as e:
        logger.error(f"Error getting forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/advisory")
def get_agricultural_advisory(
    latitude: float = Query(..., description="Farm latitude"),
    longitude: float = Query(..., description="Farm longitude"),
    crop: str = Query(None, description="Crop type for specific recommendations"),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get agricultural advisory based on current and forecast weather.
    
    Includes:
    - Irrigation recommendations
    - Pest and disease risk assessment
    - Heat/cold/wind advisories
    - Fertilizer application timing
    
    Returns:
        Agricultural recommendations and alerts
    """
    try:
        advisory = weather_service.get_agricultural_advisory(latitude, longitude, crop)
        return {"status": "success", "data": advisory}
    except Exception as e:
        logger.error(f"Error generating advisory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/combined")
def get_combined_weather_data(
    latitude: float = Query(..., description="Farm latitude"),
    longitude: float = Query(..., description="Farm longitude"),
    crop: str = Query(None, description="Crop type"),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get combined weather data: current conditions, forecast, and agricultural advisory.
    
    Convenience endpoint combining all weather information.
    
    Returns:
        Complete weather package for farm decision-making
    """
    try:
        current = weather_service.get_current_weather(latitude, longitude)
        forecast = weather_service.get_weather_forecast(latitude, longitude, days=5)
        advisory = weather_service.get_agricultural_advisory(latitude, longitude, crop)
        
        return {
            "status": "success",
            "data": {
                "current": current,
                "forecast": forecast,
                "advisory": advisory
            }
        }
    except Exception as e:
        logger.error(f"Error getting combined weather data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
