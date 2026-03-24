"""
Shared Configuration for all microservices
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Base settings for all services"""
    
    # Database Configuration
    POSTGRES_USER: str = "agentchiguru"
    POSTGRES_PASSWORD: str = "agentchiguru123"
    POSTGRES_DB: str = "agentchiguru_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    
    DATABASE_URL: Optional[str] = None
    
    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = None
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_GROUP_ID: str = "satwik-setu-group"
    
    # Qdrant Configuration
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "farming_knowledge"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "super-secret-jwt-key-change-in-production"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours
    JWT_ALGORITHM: str = "HS256"
    
    # LLM Configuration
    LLM_PROVIDER: str = "mock"  # mock, openai, ollama
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"
    
    # Service URLs (for inter-service communication)
    DISEASE_DETECTION_URL: str = "http://disease-detection:8001"
    AI_ADVISORY_URL: str = "http://ai-advisory:8002"
    IRRIGATION_URL: str = "http://irrigation:8003"
    MARKET_PRICE_URL: str = "http://market-price:8004"
    NOTIFICATION_URL: str = "http://notification:8005"
    GATEWAY_URL: str = "http://gateway:8000"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # File Upload Configuration
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    
    # Service-specific flags
    ENABLE_HEALTH_CHECK: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # Initialize Database URL if not set
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        
        # Initialize Redis URL if not set
        if not self.REDIS_URL:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# Global settings instance
settings = Settings()
