"""
SQLAlchemy Database Setup
"""
from sqlalchemy import create_engine, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator
from shared.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,  # Disable connection pooling for Firebase/serverless
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Declarative base for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI routes
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)


async def get_async_db():
    """Async database session (for async routes)"""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    
    # For async operations, we'd need different setup
    # This is a placeholder for potential async support
    pass
