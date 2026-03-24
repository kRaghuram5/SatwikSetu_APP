"""
Notification Model - stores user notifications
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from shared.database import Base


class NotificationType(PyEnum):
    """Types of notifications"""
    DISEASE_ALERT = "disease_alert"
    ADVISORY = "advisory"
    PRICE_ALERT = "price_alert"
    IRRIGATION_REMINDER = "irrigation_reminder"
    SYSTEM_ALERT = "system_alert"


class NotificationChannel(PyEnum):
    """Channels to send notifications"""
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    PUSH = "push"


class NotificationStatus(PyEnum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    # Notification details
    notification_type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    # Links
    reference_id = Column(UUID(as_uuid=True), nullable=True)  # link to advisory, upload, etc.
    # Status
    status = Column(Enum(NotificationStatus), nullable=False, default=NotificationStatus.PENDING, index=True)
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    retry_count = Column(String, nullable=True, default="0")
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Notification {self.notification_type} → {self.farmer_id}>"
