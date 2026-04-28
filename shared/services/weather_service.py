"""
Weather Service - Integration with OpenWeatherMap API
Provides current weather, forecasts, and agricultural advisories.
"""

import os
import logging
from typing import Optional, Dict, Any
import time
from datetime import datetime, timedelta
import requests


logger = logging.getLogger(__name__)


class WeatherService:
    """
    Handles weather data retrieval and caching.
    Uses OpenWeatherMap API for real-time and forecast data.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.forecast_url = f"{self.base_url}/forecast"
        self.weather_url = f"{self.base_url}/weather"
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour

    def _cache_key(self, method, lat, lon, *args):
        return f"{method}:{round(lat,3)}:{round(lon,3)}:{':'.join(str(a) for a in args)}"
    
    def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        key = self._cache_key("current", latitude, longitude)
        cached = self._get_cached(key)
        if cached:
            return cached

        try:
            params = {"lat": latitude, "lon": longitude, "appid": self.api_key, "units": "metric"}
            response = requests.get(self.weather_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            result = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "location": {"latitude": latitude, "longitude": longitude, "name": data.get("name", "Unknown")},
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "cloudiness": data["clouds"]["all"],
            "rainfall_mm": data.get("rain", {}).get("1h", 0),
            "condition": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
        }
            self._set_cached(key, result)
            return result
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return self._get_fallback_weather()

    def _get_cached(self, key):
        if key in self._cache:
            val, ts = self._cache[key]
            if time.time() - ts < self._cache_ttl:
                logger.info(f"Cache hit for key: {key}")
                return val
            else:
                logger.info(f"Cache expired for key: {key}")
        return None

    def _set_cached(self, key, val):
        self._cache[key] = (val, time.time())
        logger.info(f"Cache set for key: {key}")


    def get_weather_forecast(self, latitude: float, longitude: float, days: int = 5) -> Dict[str, Any]:
        key = self._cache_key("forecast", latitude, longitude, days)
        cached = self._get_cached(key)
        if cached:
            return cached

        try:
            params = {"lat": latitude, "lon": longitude, "appid": self.api_key, "units": "metric"}
            response = requests.get(self.forecast_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            forecast_list = data["list"]

        # Aggregate forecast by day
            daily_forecasts = {}
            for forecast in forecast_list:
                dt = datetime.utcfromtimestamp(forecast["dt"])
                day_key = dt.date().isoformat()

                if day_key not in daily_forecasts:
                    daily_forecasts[day_key] = {
                    "date": day_key,
                    "temps": [],
                    "humidity_list": [],
                    "rainfall_total": 0,
                    "wind_speeds": [],
                    "conditions": []
                }

                daily_forecasts[day_key]["temps"].append(forecast["main"]["temp"])
                daily_forecasts[day_key]["humidity_list"].append(forecast["main"]["humidity"])
                daily_forecasts[day_key]["wind_speeds"].append(forecast["wind"]["speed"])
                daily_forecasts[day_key]["rainfall_total"] += forecast.get("rain", {}).get("3h", 0)
                daily_forecasts[day_key]["conditions"].append(forecast["weather"][0]["main"])

        # Format aggregated forecast with division‑by‑zero guard
            formatted_forecast = []
            for day_key in sorted(daily_forecasts.keys())[:days]:
                day_data = daily_forecasts[day_key]
                formatted_forecast.append({
                "date": day_key,
                "avg_temp": round(sum(day_data["temps"]) / len(day_data["temps"]), 1) if day_data["temps"] else None,
                "min_temp": round(min(day_data["temps"]), 1) if day_data["temps"] else None,
                "max_temp": round(max(day_data["temps"]), 1) if day_data["temps"] else None,
                "avg_humidity": round(sum(day_data["humidity_list"]) / len(day_data["humidity_list"]), 1) if day_data["humidity_list"] else None,
                "total_rainfall_mm": round(day_data["rainfall_total"], 1),
                "avg_wind_speed": round(sum(day_data["wind_speeds"]) / len(day_data["wind_speeds"]), 1) if day_data["wind_speeds"] else None,
                "condition": max(set(day_data["conditions"]), key=day_data["conditions"].count) if day_data["conditions"] else "Unknown",
            })

            result = {
            "location": {"latitude": latitude, "longitude": longitude, "name": data["city"]["name"]},
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "forecast": formatted_forecast,
            "agricultural_advisory": self.get_agricultural_advisory(latitude, longitude)

        }
            self._set_cached(key, result)
            return result

        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            return self._get_fallback_forecast()

    def get_agricultural_advisory(
        self,
        latitude: float,
        longitude: float,
        crop: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get agricultural recommendations based on weather forecast.
        
        Args:
            latitude: Farm latitude
            longitude: Farm longitude
            crop: Crop type for specific recommendations
            
        Returns:
            Agricultural advisory with irrigation, pest, and disease risks
        """
        try:
            forecast = self.get_weather_forecast(latitude, longitude, days=5)
            current = self.get_current_weather(latitude, longitude)
            
            advisory = {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "crop": crop or "General",
                "current_conditions": {
                    "temperature": current["temperature"],
                    "humidity": current["humidity"],
                    "rainfall_today": current["rainfall_mm"]
                },
                "recommendations": self._generate_recommendations(
                    current, 
                    forecast["forecast"], 
                    crop
                ),
                "alerts": self._generate_alerts(current, forecast["forecast"]),
            }
            
            return advisory
        except Exception as e:
            logger.error(f"Error generating agricultural advisory: {e}")
            return {"error": str(e), "status": "advisory_generation_failed"}
    
    @staticmethod
    def _generate_recommendations(
        current: Dict[str, Any],
        forecast: list,
        crop: Optional[str] = None
    ) -> list:
        """Generate agricultural recommendations based on weather."""
        recommendations = []
        
        # Rainfall-based recommendations
        total_rainfall_5d = sum(day["total_rainfall_mm"] for day in forecast)
        
        if total_rainfall_5d > 50:
            recommendations.append({
                "type": "irrigation",
                "priority": "high",
                "message": f"Heavy rainfall expected ({total_rainfall_5d}mm in 5 days). Reduce or postpone irrigation.",
                "action": "Reduce scheduled irrigation by 30-40%"
            })
        elif total_rainfall_5d < 10:
            recommendations.append({
                "type": "irrigation",
                "priority": "high",
                "message": f"Minimal rainfall expected. Increase irrigation frequency.",
                "action": "Increase irrigation frequency to maintain soil moisture"
            })
        else:
            recommendations.append({
                "type": "irrigation",
                "priority": "normal",
                "message": f"Moderate rainfall expected ({total_rainfall_5d}mm). Follow standard schedule.",
                "action": "Maintain regular irrigation schedule"
            })
        
        # Temperature-based recommendations
        avg_temp = sum(day["avg_temp"] for day in forecast) / len(forecast)
        
        if avg_temp > 35:
            recommendations.append({
                "type": "crop_care",
                "priority": "high",
                "message": "High temperature stress risk",
                "action": "Increase watering frequency, apply mulch, and consider shade cloth for sensitive crops"
            })
        elif avg_temp < 10:
            recommendations.append({
                "type": "crop_care",
                "priority": "high",
                "message": "Frost risk detected",
                "action": "Protect crops from cold, consider frost protection methods"
            })
        
        # Pest and disease risk
        avg_humidity = sum(day["avg_humidity"] for day in forecast) / len(forecast)
        
        if avg_humidity > 80 and avg_temp > 20:
            recommendations.append({
                "type": "pest_disease",
                "priority": "high",
                "message": "High fungal disease risk (warm and humid conditions)",
                "action": "Monitor for fungal diseases, apply preventive fungicide if necessary"
            })
        
        if current["humidity"] > 90:
            recommendations.append({
                "type": "pest_disease",
                "priority": "medium",
                "message": "Very high humidity - pest activity likely",
                "action": "Monitor for pests, ensure good crop ventilation"
            })
        
        # Wind recommendations
        if any(day["avg_wind_speed"] > 20 for day in forecast):
            recommendations.append({
                "type": "structure",
                "priority": "medium",
                "message": "Strong winds expected",
                "action": "Check plant support structures, stake tall crops, secure structures"
            })
        
        return recommendations
    
    @staticmethod
    def _generate_alerts(
        current: Dict[str, Any],
        forecast: list
    ) -> list:
        """Generate weather alerts."""
        alerts = []
        
        # Severe weather alerts
        if current["rainfall_mm"] > 20:
            alerts.append({
                "level": "warning",
                "type": "heavy_rain",
                "message": "Heavy rain currently occurring"
            })
        
        if any(day["avg_temp"] < 0 for day in forecast):
            alerts.append({
                "level": "warning",
                "type": "frost",
                "message": "Freezing temperatures expected in forecast"
            })
        
        if any(day["avg_wind_speed"] > 40 for day in forecast):
            alerts.append({
                "level": "danger",
                "type": "severe_wind",
                "message": "Severe wind warning"
            })
        
        return alerts
    
    @staticmethod
    def _get_fallback_weather() -> Dict[str, Any]:
        """Return fallback weather data when API fails."""
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "location": {"name": "Unknown", "latitude": 0, "longitude": 0},
            "temperature": 25.0,
            "feels_like": 25.0,
            "humidity": 60,
            "pressure": 1013,
            "wind_speed": 5.0,
            "cloudiness": 50,
            "rainfall_mm": 0,
            "condition": "Partly Cloudy",
            "description": "Fallback data - API unavailable",
            "status": "fallback"
        }
    
    @staticmethod
    def _get_fallback_forecast() -> Dict[str, Any]:
        """Return fallback forecast when API fails."""
        return {
            "location": {"name": "Unknown", "latitude": 0, "longitude": 0},
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "forecast": [
                {
                    "date": (datetime.utcnow() + timedelta(days=i)).date().isoformat(),
                    "avg_temp": 25.0,
                    "min_temp": 20.0,
                    "max_temp": 30.0,
                    "avg_humidity": 65,
                    "total_rainfall_mm": 0,
                    "avg_wind_speed": 5.0,
                    "condition": "Partly Cloudy"
                }
                for i in range(5)
            ],
            "agricultural_advisory": [
                {
                    "type": "general",
                    "priority": "normal",
                    "message": "Fallback data - API unavailable",
                    "action": "Use historical data or local observations"
                }
            ],
            "status": "fallback"
        }


# Singleton instance
_weather_service = None


def get_weather_service() -> WeatherService:
    """Get or create weather service instance."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service
