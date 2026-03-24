"""
Kafka consumers for processing alert events.
Consumes from multiple topics and creates notifications.
"""

import json
import logging
import asyncio
from datetime import datetime
from aiokafka import AIOKafkaConsumer
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models.notification import Notification
from app.config import get_notification_settings
from app.channels.email import send_email_notification
from app.channels.sms import send_sms_notification

logger = logging.getLogger(__name__)
settings = get_notification_settings()

_consumer_task = None

# Topic to notification type mapping
TOPIC_TYPE_MAP = {
    "disease.detected": "disease_alert",
    "advisory.ready": "advisory",
    "price.alert": "price_alert",
    "irrigation.reminder": "irrigation",
}

# Message templates
MESSAGE_TEMPLATES = {
    "disease_alert": " Disease Alert: {disease} detected in your {crop} crop with {confidence:.0%} confidence. Please check your advisory for treatment options.",
    "advisory": " Treatment Advisory Ready: Your crop disease advisory for {disease} in {crop} is now available. View it in the app for detailed treatment and prevention steps.",
    "price_alert": " Price Alert: {crop} price at {mandi} is currently ₹{current_price}/quintal ({direction} your threshold of ₹{threshold_price}).",
    "irrigation": " Irrigation Reminder: Your {crop} field needs {water_qty_liters}L of water. {message}",
}


def format_notification_message(event_type: str, event: dict) -> str:
    """Format notification message from event data."""
    template = MESSAGE_TEMPLATES.get(event_type, " New notification: {}")
    try:
        return template.format(**event)
    except (KeyError, IndexError):
        return f" {event_type}: New update available. Check the app for details."


async def process_notification(event_type: str, event: dict):
    """Process a notification event — store in DB and dispatch via channels."""
    farmer_id = event.get("farmer_id")
    if not farmer_id:
        logger.warning(f"No farmer_id in {event_type} event — skipping notification")
        return

    message = format_notification_message(event_type, event)

    db: Session = SessionLocal()
    try:
        notification = Notification(
            farmer_id=farmer_id,
            type=event_type,
            channel="in_app",  # Default channel
            message=message,
            status="sent",
            sent_at=datetime.utcnow(),
        )
        db.add(notification)
        db.commit()
        logger.info(f"Notification created: {event_type} for farmer {farmer_id}")

        # Try email if configured
        try:
            await send_email_notification(farmer_id, event_type, message)
        except Exception as e:
            logger.debug(f"Email notification skipped: {e}")

        # Try SMS if configured
        try:
            await send_sms_notification(farmer_id, event_type, message)
        except Exception as e:
            logger.debug(f"SMS notification skipped: {e}")

    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
    finally:
        db.close()


async def consume_notifications():
    """Consume events from all notification topics."""
    topics = list(TOPIC_TYPE_MAP.keys())

    consumer = AIOKafkaConsumer(
        *topics,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="notification-group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
    )

    try:
        await consumer.start()
        logger.info(f"Notification consumer started — listening to: {topics}")

        async for msg in consumer:
            event = msg.value
            event_type = TOPIC_TYPE_MAP.get(msg.topic, "unknown")
            logger.info(f"Received {msg.topic} event")

            await process_notification(event_type, event)

    except asyncio.CancelledError:
        logger.info("Notification consumer cancelled")
    except Exception as e:
        logger.error(f"Notification consumer error: {e}")
    finally:
        await consumer.stop()


async def start_consumer():
    """Start the notification consumer as a background task."""
    global _consumer_task
    _consumer_task = asyncio.create_task(consume_notifications())


async def stop_consumer():
    """Stop the notification consumer."""
    global _consumer_task
    if _consumer_task:
        _consumer_task.cancel()
        try:
            await _consumer_task
        except asyncio.CancelledError:
            pass
