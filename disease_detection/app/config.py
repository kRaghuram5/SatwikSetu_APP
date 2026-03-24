"""Disease Detection service configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class DiseaseDetectionSettings(BaseSettings):
    DATABASE_URL: str = "postgresql://agentchiguru:agentchiguru123@postgres:5432/agentchiguru_db"
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    MODEL_PATH: str = "/app/model/plant_disease_model.pth"
    UPLOAD_DIR: str = "/app/uploads"

    class Config:
        env_file = ".env"


@lru_cache()
def get_dd_settings() -> DiseaseDetectionSettings:
    return DiseaseDetectionSettings()
