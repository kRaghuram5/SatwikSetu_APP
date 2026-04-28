"""Disease detection endpoint — accepts image, runs prediction, publishes event."""

import uuid
import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.database import get_db
from shared.models.upload import Upload
from shared.models.user import User
from shared.models.farm import Farm
from app.model.predictor import get_predictor
from app.kafka_producer import publish_disease_event
from app.config import get_dd_settings

router = APIRouter()
settings = get_dd_settings()


@router.post("/detect")
async def detect_disease(
    file: UploadFile = File(...),
    farmer_id: str = Form(...),
    farm_id: str = Form(None),
    db: Session = Depends(get_db),
):
    """
    Upload a crop image for disease detection.

    1. Save image to disk
    2. Run inference via MobileNetV2
    3. Store result in PostgreSQL
    4. Publish disease.detected event to Kafka
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    if file.content_type.lower() not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Only JPEG, PNG, or WebP images are supported. Got: {file.content_type}")

    # Read image bytes
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    # Generate upload ID and save image
    upload_id = str(uuid.uuid4())
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    image_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}.{ext}")

    with open(image_path, "wb") as f:
        f.write(image_bytes)

    # Run prediction
    predictor = get_predictor()
    result = predictor.predict(image_bytes)

    # Save to database
    upload = Upload(
        id=upload_id,
        farmer_id=farmer_id,
        farm_id=farm_id,
        image_path=image_path,
        disease_detected=result["label"],
        confidence=result["confidence"],
        crop=result["crop"],
    )
    db.add(upload)
    db.commit()

    # Publish Kafka event
    event = {
        "event": "disease.detected",
        "upload_id": upload_id,
        "farmer_id": farmer_id,
        "disease": result["disease"],
        "crop": result["crop"],
        "confidence": result["confidence"],
        "label": result["label"],
        "timestamp": datetime.utcnow().isoformat(),
    }
    await publish_disease_event(event)

    return {
        "upload_id":       upload_id,
        "disease":         result["disease"],
        "crop":            result["crop"],
        "confidence":      result["confidence"],
        "label":           result["label"],
        "is_healthy":      result["is_healthy"],
        "top_predictions": result["top_predictions"],
        "timestamp":       datetime.utcnow().isoformat(),
    }
