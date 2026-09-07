from typing import Optional, List
from datetime import date
from sqlalchemy import String, Float, JSON, Text, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class WeatherSnapshot(Base):
    __tablename__ = "weather_snapshots"

    destination: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    snapshot_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    temperature_current: Mapped[float] = mapped_column(Float, default=25.0)
    temperature_min: Mapped[float] = mapped_column(Float, default=20.0)
    temperature_max: Mapped[float] = mapped_column(Float, default=30.0)
    condition: Mapped[str] = mapped_column(String(64), default="Sunny")  # Sunny, Rainy, Cloudy, Thunderstorm, etc.
    rain_probability: Mapped[float] = mapped_column(Float, default=10.0)
    humidity: Mapped[float] = mapped_column(Float, default=65.0)
    wind_speed_kmh: Mapped[float] = mapped_column(Float, default=12.0)
    uv_index: Mapped[float] = mapped_column(Float, default=5.0)
    hourly_forecast: Mapped[Optional[List[dict]]] = mapped_column(JSON, default=list)
    daily_forecast: Mapped[Optional[List[dict]]] = mapped_column(JSON, default=list)
    travel_advisories: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
