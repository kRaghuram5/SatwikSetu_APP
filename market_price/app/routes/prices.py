"""Market price endpoints — query mandi prices with Redis caching."""

import json
import redis
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from shared.database import get_db
from shared.models.market_price import MarketPrice
from app.config import get_mp_settings

router = APIRouter()
settings = get_mp_settings()

# Redis client for caching
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception:
    redis_client = None


@router.get("/market-prices")
def get_market_prices(
    crop: str = Query(..., description="Crop name (e.g., Rice, Wheat, Tomato)"),
    state: str = Query(None, description="State name (e.g., Karnataka, Maharashtra)"),
    db: Session = Depends(get_db),
):
    """
    Fetch current mandi prices for a crop, optionally filtered by state.
    Results are cached in Redis for 6 hours.
    """
    # Check cache
    cache_key = f"market:{crop.lower()}:{(state or 'all').lower()}"
    if redis_client:
        try:
            cached = redis_client.get(cache_key)
            if cached:
                result = json.loads(cached)
                result["cached"] = True
                return result
        except Exception:
            pass

    # Query database
    query = db.query(MarketPrice).filter(
        func.lower(MarketPrice.crop) == crop.lower()
    )
    if state:
        query = query.filter(func.lower(MarketPrice.state) == state.lower())

    prices = query.order_by(MarketPrice.price_date.desc()).all()

    if not prices:
        return {
            "crop": crop,
            "state": state,
            "prices": [],
            "message": "No price data found for the given crop/state combination",
        }

    price_list = [
        {
            "mandi": p.mandi,
            "state": p.state,
            "price_per_quintal": p.price_per_quintal,
            "date": p.price_date.isoformat() if p.price_date else None,
        }
        for p in prices
    ]

    # Calculate statistics
    price_values = [p.price_per_quintal for p in prices]
    avg_price = round(sum(price_values) / len(price_values), 2)
    min_price = min(price_values)
    max_price = max(price_values)

    # Simple trend analysis
    if len(price_values) >= 2:
        trend = "rising" if price_values[0] > price_values[-1] else "falling" if price_values[0] < price_values[-1] else "stable"
    else:
        trend = "stable"

    result = {
        "crop": crop.title(),
        "state": state or "All India",
        "prices": price_list,
        "statistics": {
            "average_price": avg_price,
            "min_price": min_price,
            "max_price": max_price,
            "num_mandis": len(price_list),
        },
        "trend": trend,
    }

    # Cache result for 6 hours
    if redis_client:
        try:
            redis_client.setex(cache_key, 21600, json.dumps(result, default=str))
        except Exception:
            pass

    result["cached"] = False
    return result


@router.get("/market-prices/crops")
def list_available_crops(db: Session = Depends(get_db)):
    """List all crops with price data available."""
    crops = db.query(MarketPrice.crop).distinct().all()
    return {"crops": sorted(set(c[0] for c in crops))}


@router.get("/market-prices/states")
def list_available_states(
    crop: str = Query(None, description="Filter states by crop"),
    db: Session = Depends(get_db),
):
    """List all states with price data, optionally filtered by crop."""
    query = db.query(MarketPrice.state).distinct()
    if crop:
        query = query.filter(func.lower(MarketPrice.crop) == crop.lower())
    states = query.all()
    return {"states": sorted(set(s[0] for s in states))}
