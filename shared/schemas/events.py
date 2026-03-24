"""
Kafka Event Schema - Pydantic models for event streaming
"""
from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime
import uuid


# ==================== Disease Detection Events ====================

class DiseaseDetectedEvent(BaseModel):
    """Published by Disease Detection when an image is analyzed."""
    event: str = "disease.detected"
    upload_id: str
    farmer_id: str
    disease: str
    crop: str
    confidence: float
    location: Optional[str] = None
    timestamp: datetime = None

    def __init__(self, **data):
        if data.get("timestamp") is None:
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)


# ==================== AI Advisory Events ====================

class AdvisoryReadyEvent(BaseModel):
    """Published by AI Advisory after generating treatment advice."""
    event: str = "advisory.ready"
    upload_id: str
    farmer_id: str
    disease: str
    crop: str
    advisory_id: str
    summary: str
    timestamp: datetime = None

    def __init__(self, **data):
        if data.get("timestamp") is None:
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)


# ==================== Irrigation Events ====================

class IrrigationReminderEvent(BaseModel):
    """Published by Irrigation service for scheduled reminders."""
    event: str = "irrigation.reminder"
    farm_id: str
    farmer_id: str
    crop: str
    water_qty_liters: float
    message: str
    timestamp: datetime = None

    def __init__(self, **data):
        if data.get("timestamp") is None:
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)


# ==================== Market Price Events ====================

class PriceAlertEvent(BaseModel):
    """Published by Market Price when a price threshold is crossed."""
    event: str = "price.alert"
    crop: str
    state: str
    mandi: str
    current_price: float
    threshold_price: float
    direction: str  # "above" or "below"
    timestamp: datetime = None

    def __init__(self, **data):
        if data.get("timestamp") is None:
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)


# ==================== Notification Events ====================

class NotificationSendEvent(BaseModel):
    """Event to send notification"""
    event: str = "notification.send"
    farmer_id: str
    notification_type: str  # disease_alert, advisory, price_alert, irrigation_reminder
    channel: str  # email, sms, in_app, push
    title: str
    message: str
    reference_id: Optional[str]  # link to advisory, upload, etc.
    timestamp: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "event": "notification.send",
                "farmer_id": "123e4567-e89b-12d3-a456-426614174001",
                "notification_type": "disease_alert",
                "channel": "email",
                "title": "Disease Alert: Early Blight Detected",
                "message": "Early Blight has been detected on your tomato crop...",
                "reference_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-03-24T10:30:00Z"
            }
        }
