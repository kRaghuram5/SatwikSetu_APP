"""
Rule-based irrigation engine.
Determines water quantity, frequency, and recommendations based on
crop type, growth stage, soil moisture, and temperature.
"""

from typing import Optional
from datetime import datetime, timedelta


# ── Irrigation Rules Knowledge Base ──
IRRIGATION_RULES = {
    "rice": {
        "vegetative": {
            "base_water": 5000,    # L/ha
            "frequency": "Daily",
            "moisture_threshold": 40,
            "temp_threshold": 30,
            "tips": [
                "Maintain 5cm standing water in paddies",
                "Monitor drainage channels",
                "Apply nitrogen fertilizer before irrigation",
            ],
        },
        "flowering": {
            "base_water": 6000,
            "frequency": "Daily",
            "moisture_threshold": 50,
            "temp_threshold": 28,
            "tips": [
                "Critical stage — do not let fields dry",
                "Maintain 5-7cm water depth",
                "Avoid draining during anthesis",
            ],
        },
        "ripening": {
            "base_water": 3000,
            "frequency": "Alternate days",
            "moisture_threshold": 35,
            "temp_threshold": 30,
            "tips": [
                "Gradually reduce water",
                "Drain field 2 weeks before harvest",
                "Monitor grain moisture content",
            ],
        },
    },
    "wheat": {
        "tillering": {
            "base_water": 3000,
            "frequency": "Every 3 days",
            "moisture_threshold": 35,
            "temp_threshold": 25,
            "tips": [
                "Crown root initiation — critical irrigation",
                "Light irrigation preferred",
                "Avoid waterlogging",
            ],
        },
        "flowering": {
            "base_water": 4000,
            "frequency": "Every 2 days",
            "moisture_threshold": 40,
            "temp_threshold": 28,
            "tips": [
                "Most critical stage for wheat yield",
                "Ensure uniform water distribution",
                "Combine with foliar nutrient spray",
            ],
        },
        "grain_filling": {
            "base_water": 3500,
            "frequency": "Every 3 days",
            "moisture_threshold": 35,
            "temp_threshold": 30,
            "tips": [
                "Maintain moisture for proper grain development",
                "Avoid excess water",
                "Monitor for lodging",
            ],
        },
    },
    "tomato": {
        "vegetative": {
            "base_water": 3500,
            "frequency": "Every 2 days",
            "moisture_threshold": 40,
            "temp_threshold": 28,
            "tips": [
                "Use drip irrigation for best results",
                "Mulch to conserve moisture",
                "Avoid wetting foliage",
            ],
        },
        "flowering": {
            "base_water": 4000,
            "frequency": "Daily",
            "moisture_threshold": 45,
            "temp_threshold": 30,
            "tips": [
                "Consistent moisture prevents blossom end rot",
                "Water deeply but infrequently",
                "Morning irrigation preferred",
            ],
        },
        "fruiting": {
            "base_water": 4500,
            "frequency": "Daily",
            "moisture_threshold": 45,
            "temp_threshold": 32,
            "tips": [
                "Maximum water demand during fruit development",
                "Ensure even moisture — prevent fruit cracking",
                "Consider fertigation with calcium",
            ],
        },
    },
    "potato": {
        "vegetative": {
            "base_water": 3000,
            "frequency": "Every 2 days",
            "moisture_threshold": 40,
            "temp_threshold": 25,
            "tips": [
                "Begin irrigation after planting",
                "Light but frequent irrigation",
                "Avoid waterlogging in heavy soils",
            ],
        },
        "tuber_initiation": {
            "base_water": 4500,
            "frequency": "Daily",
            "moisture_threshold": 50,
            "temp_threshold": 28,
            "tips": [
                "Most critical stage — maintain consistent moisture",
                "Uneven moisture causes misshapen tubers",
                "Hill up soil after irrigation",
            ],
        },
        "maturation": {
            "base_water": 2500,
            "frequency": "Every 3 days",
            "moisture_threshold": 30,
            "temp_threshold": 28,
            "tips": [
                "Reduce irrigation gradually",
                "Stop irrigation 2 weeks before harvest",
                "Allow skin to set for storage",
            ],
        },
    },
}

# Default for unknown crops
DEFAULT_RULE = {
    "base_water": 3000,
    "frequency": "Every 2 days",
    "moisture_threshold": 40,
    "temp_threshold": 28,
    "tips": [
        "Monitor soil moisture regularly",
        "Water deeply but less frequently",
        "Adjust based on weather conditions",
    ],
}


def get_irrigation_recommendation(
    crop: str,
    soil_moisture: Optional[float] = None,
    temperature: Optional[float] = None,
    growth_stage: Optional[str] = None,
) -> dict:
    """
    Generate irrigation recommendation based on input parameters.

    Returns a recommendation dict with water quantity, frequency,
    urgency, next irrigation time, and practical tips.
    """
    crop_lower = crop.lower()
    stage = (growth_stage or "vegetative").lower()

    # Look up rules
    crop_rules = IRRIGATION_RULES.get(crop_lower, {})
    rule = crop_rules.get(stage, DEFAULT_RULE)

    base_water = rule["base_water"]
    frequency = rule["frequency"]
    tips = rule["tips"]

    # Adjust water based on conditions
    adjustment_factor = 1.0
    urgency = "normal"
    recommendation = "Follow scheduled irrigation"

    if soil_moisture is not None:
        if soil_moisture < rule["moisture_threshold"] - 15:
            adjustment_factor = 1.3
            urgency = "urgent"
            recommendation = "Irrigate immediately — soil moisture critically low"
        elif soil_moisture < rule["moisture_threshold"]:
            adjustment_factor = 1.1
            urgency = "high"
            recommendation = "Irrigate within 6 hours — moisture below threshold"
        elif soil_moisture > rule["moisture_threshold"] + 20:
            adjustment_factor = 0.7
            urgency = "low"
            recommendation = "Reduce irrigation — adequate moisture available"

    if temperature is not None:
        if temperature > rule["temp_threshold"] + 5:
            adjustment_factor *= 1.2
            tips = tips + ["Irrigate during early morning or late evening to reduce evaporation"]
        elif temperature < rule["temp_threshold"] - 10:
            adjustment_factor *= 0.8

    final_water = round(base_water * adjustment_factor)

    # Calculate next irrigation
    freq_hours = {
        "Daily": 24,
        "Every 2 days": 48,
        "Every 3 days": 72,
        "Alternate days": 48,
    }
    next_hours = freq_hours.get(frequency, 48)
    if urgency == "urgent":
        next_hours = 0
    elif urgency == "high":
        next_hours = 6

    next_irrigation = datetime.utcnow() + timedelta(hours=next_hours)

    return {
        "crop": crop.title(),
        "growth_stage": stage,
        "recommendation": recommendation,
        "urgency": urgency,
        "water_quantity_liters_per_hectare": final_water,
        "frequency": frequency,
        "soil_moisture_input": soil_moisture,
        "temperature_input": temperature,
        "moisture_threshold": rule["moisture_threshold"],
        "next_irrigation": next_irrigation.isoformat() + "Z",
        "tips": tips,
    }
