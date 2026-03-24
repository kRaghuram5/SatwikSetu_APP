"""
Market Price Model - stores mandi prices for crops
"""
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from shared.database import Base


class MarketPrice(Base):
    __tablename__ = "market_prices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    crop = Column(String(50), nullable=False, index=True)
    state = Column(String(50), nullable=False, index=True)
    mandi = Column(String(100), nullable=False)  # Market/Mandi name
    # Price information
    price_per_quintal = Column(Float, nullable=False)
    price_per_kg = Column(Float, nullable=True)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    # Metadata
    price_date = Column(DateTime, nullable=False, index=True)
    fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    source = Column(String(100), nullable=True)  # API source, agrimarket, etc.
    
    def __repr__(self):
        return f"<MarketPrice {self.crop} @ {self.mandi}>"
