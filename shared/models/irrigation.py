"""
Irrigation Model - stores irrigation recommendations and history
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from shared.database import Base


class GrowthStage(PyEnum):
    """Crop growth stages"""
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURATION = "maturation"


class IrrigationLog(Base):
    __tablename__ = "irrigation_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    farm_id = Column(UUID(as_uuid=True), ForeignKey("farms.id"), nullable=False, index=True)
    crop = Column(String(50), nullable=False)
    growth_stage = Column(Enum(GrowthStage), nullable=False)
    # Sensor data
    soil_moisture = Column(Float, nullable=False)  # percentage 0-100
    temperature = Column(Float, nullable=False)  # in Celsius
    rainfall = Column(Float, nullable=True)  # in mm
    # Recommendation
    water_qty_liters_per_hectare = Column(Float, nullable=False)
    frequency_days = Column(Float, nullable=True)  # irrigation frequency
    irrigation_method = Column(String(50), nullable=True)  # drip, flood, sprinkler
    # Metadata
    recommended_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    is_applied = Column(DateTime, nullable=True)  # When farmer applied irrigation
    notes = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<IrrigationLog {self.id}>"
