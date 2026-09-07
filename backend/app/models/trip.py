from typing import Optional, List
from datetime import date, time
from sqlalchemy import String, Float, Integer, JSON, ForeignKey, Text, Date, Time, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class TripStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class Trip(Base):
    __tablename__ = "trips"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, default=1)
    travelers_count: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default=TripStatus.PLANNED.value)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    travel_style: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Financials
    total_budget: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    actual_cost: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="BDT")
    
    # Flags & Meta
    is_favorite: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    packing_list: Mapped[List[str]] = mapped_column(JSON, default=list)
    weather_summary: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="trips")
    days: Mapped[List["TripDay"]] = relationship("TripDay", back_populates="trip", cascade="all, delete-orphan", order_by="TripDay.day_number")
    budget_record: Mapped[Optional["Budget"]] = relationship("Budget", back_populates="trip", uselist=False, cascade="all, delete-orphan")


class TripDay(Base):
    __tablename__ = "trip_days"

    trip_id: Mapped[str] = mapped_column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), index=True)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    theme: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weather_forecast: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    estimated_day_cost: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="days")
    activities: Mapped[List["Activity"]] = relationship("Activity", back_populates="trip_day", cascade="all, delete-orphan", order_by="Activity.order_index")


class Activity(Base):
    __tablename__ = "activities"

    trip_day_id: Mapped[str] = mapped_column(String(36), ForeignKey("trip_days.id", ondelete="CASCADE"), index=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(64), default="attraction")  # attraction, meal, hotel, transport, leisure
    location_name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    start_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # "09:00"
    end_time: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)    # "11:30"
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="BDT")
    travel_time_from_previous_minutes: Mapped[int] = mapped_column(Integer, default=0)
    travel_mode: Mapped[Optional[str]] = mapped_column(String(64), default="drive")  # walk, drive, transit
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_indoor: Mapped[bool] = mapped_column(default=False)
    is_completed: Mapped[bool] = mapped_column(default=False)

    # Relationships
    trip_day: Mapped["TripDay"] = relationship("TripDay", back_populates="activities")


class SavedPlace(Base):
    __tablename__ = "saved_places"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="place")
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="saved_places")
