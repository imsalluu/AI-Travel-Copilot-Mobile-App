from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class HourlyForecastSchema(BaseModel):
    time_str: str
    temperature: float
    rain_probability: float
    condition: str


class ForecastDaySchema(BaseModel):
    forecast_date: date
    temperature_min: float
    temperature_max: float
    condition: str
    rain_probability: float
    uv_index: float
    travel_friendly: bool
    indoor_recommended: bool


class WeatherResponse(BaseModel):
    destination: str
    current_temperature: float
    condition: str
    rain_probability: float
    humidity: float
    wind_speed_kmh: float
    uv_index: float
    travel_advisories: List[str] = []
    is_rainy: bool = False
    daily_forecasts: List[ForecastDaySchema] = []
    hourly_forecasts: List[HourlyForecastSchema] = []
    indoor_alternatives_suggested: bool = False
