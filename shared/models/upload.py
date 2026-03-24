"""
Upload Model - for storing image uploads and disease detection results
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from shared.database import Base


class Upload(Base):
    __tablename__ = "uploads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    farm_id = Column(UUID(as_uuid=True), ForeignKey("farms.id"), nullable=True)
    image_path = Column(String(255), nullable=False)
    image_filename = Column(String(255), nullable=False)
    # Disease detection results
    disease_detected = Column(String(100), nullable=True)
    confidence = Column(Float, nullable=True)  # 0.0 - 1.0
    crop = Column(String(50), nullable=False)
    # Metadata
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    processed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Upload {self.id}>"
