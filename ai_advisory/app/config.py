"""AI Advisory service configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class AdvisorySettings(BaseSettings):
    DATABASE_URL: str = "postgresql://agentchiguru:agentchiguru123@postgres:5432/agentchiguru_db"
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    LLM_PROVIDER: str = "openai"  # openai
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"
    KNOWLEDGE_BASE_DIR: str = "data/knowledge_base"

    class Config:
        env_file = ".env"


@lru_cache()
def get_advisory_settings() -> AdvisorySettings:
    return AdvisorySettings()
