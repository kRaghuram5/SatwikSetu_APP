"""
Farm Model
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from shared.database import Base


class Farm(Base):
    __tablename__ = "farms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    crop_type = Column(String(50), nullable=False)  # rice, wheat, cotton, etc.
    area_hectares = Column(Float, nullable=False)  # Farm size
    soil_type = Column(String(50), nullable=True)  # clay, sandy, loamy
    location = Column(String(255), nullable=True)  # GPS coordinates or address
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Farm {self.name}>"
