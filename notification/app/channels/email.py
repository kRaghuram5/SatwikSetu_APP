"""Email notification channel — sends via SMTP when configured."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sqlalchemy import select
from shared.database import SessionLocal
from shared.models.user import User

logger = logging.getLogger(__name__)


def _get_farmer_email(farmer_id: str) -> str | None:
    """Look up the farmer's email address from the users table."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == farmer_id, User.is_active == True).first()
        return user.email if user else None
    finally:
        db.close()


async def send_email_notification(farmer_id: str, event_type: str, message: str):
    """Send email notification to a farmer via SMTP."""
    from app.config import get_notification_settings
    settings = get_notification_settings()

    if not settings.SMTP_HOST:
        logger.debug("Email channel not configured — logging instead")
        logger.info(f" EMAIL → Farmer {farmer_id}: [{event_type}] {message[:100]}...")
        return

    recipient = _get_farmer_email(farmer_id)
    if not recipient:
        logger.warning(f"No email found for farmer {farmer_id} — skipping email")
        return

    subject_map = {
        "disease_alert": "Disease Alert — Agent Chiguru",
        "advisory": "Treatment Advisory — Agent Chiguru",
        "price_alert": "Price Alert — Agent Chiguru",
        "irrigation": "Irrigation Reminder — Agent Chiguru",
    }
    subject = subject_map.get(event_type, "Notification — Agent Chiguru")

    from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = recipient
    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(from_email, recipient, msg.as_string())
        logger.info(f"Email sent to {recipient} for {event_type}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")
