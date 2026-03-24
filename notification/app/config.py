"""Notification service configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class NotificationSettings(BaseSettings):
    DATABASE_URL: str = "postgresql://agentchiguru:agentchiguru123@postgres:5432/agentchiguru_db"
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_notification_settings() -> NotificationSettings:
    return NotificationSettings()
