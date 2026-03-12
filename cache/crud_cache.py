from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
import uuid
import json
import logging
import redis

from models import ProductCreate, ProductUpdate, ProductResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_URL = "redis://localhost:6579/1"
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

CACHE_TTL = 300  # Cache time-to-live in seconds
CACHE_PREFIX = "product_cache"  # Prefix for cache keys

def cache_key(product_id: uuid.UUID) -> str:
    return f"{CACHE_PREFIX}:{str(product_id)}"

def serialize_product(data: dict) -> str:
    return json.dumps(data)

def deserialize_product(data: str) -> dict:
    return json.loads(data)


app = FastAPI(
    title="CRUD with Redis (Cache only)",
    description="Operations directly on Redis Key-Value Store"
)

@app.on_event("startup")
def startup():
    try:
        redis_client.ping()
        logger.info("Connected to Redis successfully.")
    except redis.ConnectionError:
        logger.error(f"Failed to connect to Redis")

# --Create --

@app.post("/products/", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate):
    product_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    product_data = {
        "id": product_id,
        "name": product.name,
        "category": product.category,
        "price": product.price,
        "description": product.description,
        "created_at": timestamp,
        "updated_at": timestamp,
        "source": "redis_cache"
    }
    try:
        redis_client.setex(
            cache_key(product_id),
            CACHE_TTL,
            serialize_product(product_data)
        )
        logger.info(f"Product created and cached with ID: {product_id}")
    except redis.ConnectionError:
        raise HTTPException(status_code=503,detail="Redis unavailable")
    return product_data

#--read one---
@app.get("/products/{product_id}", response_model=ProductResponse)
def read_product(product_id: uuid.UUID):
    try:
        cached_product = redis_client.get(cache_key(product_id))
        if cached_product:
            logger.info(f"Product retrieved from cache with ID: {product_id}")
            return deserialize_product(cached_product)
    except redis.ConnectionError:
        raise HTTPException(status_code=503,detail="Redis unavailable")
    
    raise HTTPException(status_code=404, detail="Product not found in cache")


