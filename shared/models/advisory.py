"""
Advisory Model - stores AI-generated recommendations
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from shared.database import Base


class Advisory(Base):
    __tablename__ = "advisories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.id"), nullable=False, unique=True, index=True)
    disease = Column(String(100), nullable=False)
    crop = Column(String(50), nullable=False)
    # Recommendations
    treatment = Column(Text, nullable=False)  # Detailed treatment advice
    organic_alternative = Column(Text, nullable=True)
    prevention = Column(JSON, nullable=True)  # List of prevention tips
    fertilizer = Column(String(255), nullable=True)
    pesticide = Column(String(255), nullable=True)
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    model_name = Column(String(100), nullable=True)  # Which LLM generated this
    
    def __repr__(self):
        return f"<Advisory {self.id}>"
