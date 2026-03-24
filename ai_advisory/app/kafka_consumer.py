"""Kafka consumer for disease.detected events — triggers RAG pipeline."""

import json
import logging
import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models.advisory import Advisory
from app.rag.chain import get_advisory_chain
from app.config import get_advisory_settings

logger = logging.getLogger(__name__)
settings = get_advisory_settings()

_consumer_task = None


async def consume_disease_events():
    """
    Continuously consume disease.detected events and generate advisories.

    Flow:
    1. Consume disease.detected from Kafka
    2. Run RAG chain to generate advisory
    3. Store advisory in PostgreSQL
    4. Publish advisory.ready event
    """
    consumer = AIOKafkaConsumer(
        "disease.detected",
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="ai-advisory-group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
    )

    try:
        await consumer.start()
        await producer.start()
        logger.info("Advisory Kafka consumer started")

        async for msg in consumer:
            event = msg.value
            logger.info(f"Received disease.detected: {event.get('upload_id')}")

            try:
                # Generate advisory using RAG
                chain = get_advisory_chain()
                advisory_data = await chain.generate_advisory(
                    disease=event.get("disease", "Unknown"),
                    crop=event.get("crop", "Unknown"),
                    confidence=event.get("confidence", 0.0),
                    location=event.get("location"),
                )

                # Store in database
                db: Session = SessionLocal()
                try:
                    advisory = Advisory(
                        upload_id=event["upload_id"],
                        treatment=advisory_data.get("treatment", ""),
                        organic_alternative=advisory_data.get("organic_alternative", ""),
                        prevention=json.dumps(advisory_data.get("prevention", [])),
                        fertilizer=advisory_data.get("fertilizer", ""),
                    )
                    db.add(advisory)
                    db.commit()
                    db.refresh(advisory)

                    # Publish advisory.ready
                    ready_event = {
                        "event": "advisory.ready",
                        "upload_id": event["upload_id"],
                        "farmer_id": event.get("farmer_id"),
                        "disease": event.get("disease"),
                        "crop": event.get("crop"),
                        "advisory_id": str(advisory.id),
                        "summary": advisory_data.get("treatment", "")[:200],
                    }
                    await producer.send_and_wait("advisory.ready", value=ready_event)
                    logger.info(f"Advisory generated for upload {event['upload_id']}")

                finally:
                    db.close()

            except Exception as e:
                logger.error(f"Error processing disease event: {e}")

    except asyncio.CancelledError:
        logger.info("Advisory consumer cancelled")
    except Exception as e:
        logger.error(f"Advisory consumer error: {e}")
    finally:
        await consumer.stop()
        await producer.stop()


async def start_consumer():
    """Start the Kafka consumer as a background task."""
    global _consumer_task
    _consumer_task = asyncio.create_task(consume_disease_events())


async def stop_consumer():
    """Stop the Kafka consumer."""
    global _consumer_task
    if _consumer_task:
        _consumer_task.cancel()
        try:
            await _consumer_task
        except asyncio.CancelledError:
            pass
