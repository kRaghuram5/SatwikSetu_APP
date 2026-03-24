"""Irrigation service configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class IrrigationSettings(BaseSettings):
    DATABASE_URL: str = "postgresql://agentchiguru:agentchiguru123@postgres:5432/agentchiguru_db"
    REDIS_URL: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"


@lru_cache()
def get_irrigation_settings() -> IrrigationSettings:
    return IrrigationSettings()
