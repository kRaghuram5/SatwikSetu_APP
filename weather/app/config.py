"""Weather service configuration."""

import os
from pydantic_settings import BaseSettings


class WeatherSettings(BaseSettings):
    """Weather service settings."""
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "demo_key_replace_me")
    WEATHER_CACHE_TTL: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = True


def get_weather_settings() -> WeatherSettings:
    """Get weather settings."""
    return WeatherSettings()
