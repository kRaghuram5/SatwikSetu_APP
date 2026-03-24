"""SMS notification channel (placeholder — configurable via Twilio/SNS)."""

import logging

logger = logging.getLogger(__name__)


async def send_sms_notification(farmer_id: str, event_type: str, message: str):
    """
    Send SMS notification to a farmer.

    In production, integrate with:
    - Twilio
    - AWS SNS
    - MSG91 (India)

    For the workshop, this logs the notification.
    """
    logger.info(f" SMS → Farmer {farmer_id}: [{event_type}] {message[:80]}...")

    # Production Twilio example:
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # client.messages.create(body=message, from_='+1234567890', to=farmer_phone)
