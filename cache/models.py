from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    description: Optional[str] = None

class ProductUpdate(ProductCreate):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None

class ProductResponse(ProductCreate):
    id: uuid.UUID
    name: str
    category: str
    price: float
    description: Optional[str] = None
    created_at: datetime | str
    updated_at: datetime | str
    source: str = "database"

    class Config:
        from_attributes = True
        