"""
 Notification Service — Agent Chiguru AI
===========================================
Kafka-powered multi-channel notification service.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.consumers.alert_consumer import start_consumer, stop_consumer

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start Kafka consumer on startup, stop on shutdown."""
    await start_consumer()
    yield
    await stop_consumer()


app = FastAPI(
    title=" Notification Service",
    description="Kafka-powered alerts via email, SMS, and in-app notifications",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"service": "notification", "status": "healthy"}


@app.get("/notifications/{farmer_id}")
async def get_notifications(farmer_id: str):
    """Retrieve recent notifications for a farmer (last 20)."""
    from sqlalchemy.orm import Session
    from shared.database import SessionLocal
    from shared.models.notification import Notification

    db: Session = SessionLocal()
    try:
        notifications = (
            db.query(Notification)
            .filter(Notification.farmer_id == farmer_id)
            .order_by(Notification.created_at.desc())
            .limit(20)
            .all()
        )
        return {
            "farmer_id": farmer_id,
            "count": len(notifications),
            "notifications": [
                {
                    "id": str(n.id),
                    "type": n.type,
                    "channel": n.channel,
                    "message": n.message,
                    "status": n.status,
                    "created_at": n.created_at.isoformat() if n.created_at else None,
                }
                for n in notifications
            ],
        }
    finally:
        db.close()
