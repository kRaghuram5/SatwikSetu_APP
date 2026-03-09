from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
import uuid
import random
import os
import shutil

from ingestion import Event, KafkaEventProducer

app = FastAPI()
app_v1 = APIRouter(prefix="/api/v1", tags=["v1"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app_v1.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    prediction_id = str(uuid.uuid4())
    image_path = f"{UPLOAD_DIR}/{prediction_id}_{file.filename}"

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    isDisease = random.choice([True, False])

    event = Event(prediction_id=prediction_id, image_path=image_path, isDisease=isDisease)
    producer = KafkaEventProducer()
    await producer.publish_event(event)

    return {"prediction_id": prediction_id, "image_path": image_path, "isDisease": isDisease}


app.include_router(app_v1)