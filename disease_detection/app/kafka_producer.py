"""Kafka producer for publishing disease detection events."""

import json
import logging
from aiokafka import AIOKafkaProducer
from app.config import get_dd_settings

logger = logging.getLogger(__name__)

_producer: AIOKafkaProducer = None


async def get_kafka_producer() -> AIOKafkaProducer:
    """Get or create the Kafka producer singleton."""
    global _producer
    if _producer is None:
        settings = get_dd_settings()
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        )
        try:
            await _producer.start()
            logger.info("Kafka producer started")
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            _producer = None
    return _producer


async def close_kafka_producer():
    """Gracefully close the Kafka producer."""
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None
        logger.info("Kafka producer stopped")


async def publish_disease_event(event_data: dict):
    """Publish a disease.detected event to Kafka."""
    producer = await get_kafka_producer()
    if producer:
        try:
            await producer.send_and_wait("disease.detected", value=event_data)
            logger.info(f"Published disease.detected event: {event_data.get('upload_id')}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
    else:
        logger.warning("Kafka producer unavailable — event not published")
