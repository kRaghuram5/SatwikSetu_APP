"""
API Response Schemas - Pydantic models for advisory responses
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class AdvisoryResponse(BaseModel):
    """Advisory response schema"""
    id: UUID
    upload_id: UUID
    disease: str
    crop: str
    treatment: str
    prevention: str
    organic_alternative: str
    pesticide: str
    fertilizer: str
    model_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "upload_id": "550e8400-e29b-41d4-a716-446655440001",
                "disease": "Early Blight",
                "crop": "Tomato",
                "treatment": "Apply fungicide spray every 7-10 days. Remove infected leaves...",
                "prevention": "Ensure proper spacing, avoid overhead irrigation...",
                "organic_alternative": "Neem oil 5% spray at 7-day intervals",
                "pesticide": "Mancozeb 0.75% or Chlorothalonil 2.5 g/L",
                "fertilizer": "NPK 10-10-10 with potassium sulfate for resistance",
                "model_name": "RAG-LangChain",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class AdvisoryCreateRequest(BaseModel):
    """Request to manually trigger advisory generation"""
    upload_id: UUID
    disease: str
    crop: str
    symptoms: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "upload_id": "550e8400-e29b-41d4-a716-446655440001",
                "disease": "Early Blight",
                "crop": "Tomato",
                "symptoms": "Brown spots with concentric rings on leaves"
            }
        }


class AdvisoryStatistics(BaseModel):
    """Advisory statistics response"""
    total_advisories: int
    top_diseases: list[dict]
    top_crops: list[dict]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_advisories": 150,
                "top_diseases": [
                    {"disease": "Early Blight", "count": 45},
                    {"disease": "Powdery Mildew", "count": 38}
                ],
                "top_crops": [
                    {"crop": "Tomato", "count": 60},
                    {"crop": "Wheat", "count": 45}
                ]
            }
        }
