from datetime import date
from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.weather import WeatherResponse
from app.services.weather_service import weather_service

router = APIRouter()


@router.get("", response_model=WeatherResponse)
async def get_destination_weather(
    destination: str = Query(..., description="Destination name (e.g. Cox's Bazar, Sylhet)"),
    start_date: Optional[date] = Query(None, description="Trip start date"),
    duration_days: int = Query(3, ge=1, le=14, description="Trip duration in days"),
):
    """Retrieve weather forecast, rain probability, and AI travel advisories for a destination."""
    weather_data = await weather_service.get_weather_for_destination(
        destination=destination,
        start_date=start_date,
        duration_days=duration_days,
    )
    return weather_data
