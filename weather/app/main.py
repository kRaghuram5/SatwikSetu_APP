"""Weather service main application."""

from fastapi import FastAPI
from weather.app.routes.weather import router as weather_router

app = FastAPI(
    title="Weather Service",
    description="Real-time weather data and agricultural advisories",
    version="1.0.0"
)

app.include_router(weather_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "weather"}
