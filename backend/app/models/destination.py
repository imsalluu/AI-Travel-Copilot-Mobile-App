from typing import Optional, List
from sqlalchemy import String, Float, Integer, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Destination(Base):
    __tablename__ = "destinations"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    country: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    best_time_to_visit: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    climate: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="BDT")
    average_daily_cost: Mapped[float] = mapped_column(Float, default=5000.0)
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    gallery: Mapped[List[str]] = mapped_column(JSON, default=list)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)  # ["beach", "mountains", "scenic", "nature"]
    safety_rating: Mapped[float] = mapped_column(Float, default=4.5)

    # Relationships
    places: Mapped[List["Place"]] = relationship("Place", back_populates="destination", cascade="all, delete-orphan")
    hotels: Mapped[List["Hotel"]] = relationship("Hotel", back_populates="destination", cascade="all, delete-orphan")
    restaurants: Mapped[List["Restaurant"]] = relationship("Restaurant", back_populates="destination", cascade="all, delete-orphan")


class Place(Base):
    __tablename__ = "places"

    destination_id: Mapped[str] = mapped_column(String(36), ForeignKey("destinations.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(64), index=True)  # beach, museum, park, viewpoint, temple, waterfall
    description: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=4.5)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0)
    typical_duration_minutes: Mapped[int] = mapped_column(Integer, default=90)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="BDT")
    opening_hours: Mapped[Optional[str]] = mapped_column(String(255), default="09:00 - 18:00")
    is_indoor: Mapped[bool] = mapped_column(default=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)

    # Relationships
    destination: Mapped["Destination"] = relationship("Destination", back_populates="places")


class Hotel(Base):
    __tablename__ = "hotels"

    destination_id: Mapped[str] = mapped_column(String(36), ForeignKey("destinations.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="hotel")  # resort, hotel, hostel, guesthouse, boutique
    star_rating: Mapped[float] = mapped_column(Float, default=4.0)
    rating: Mapped[float] = mapped_column(Float, default=4.5)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    price_per_night: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="BDT")
    amenities: Mapped[List[str]] = mapped_column(JSON, default=list)  # ["wifi", "pool", "breakfast", "sea_view"]
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Relationships
    destination: Mapped["Destination"] = relationship("Destination", back_populates="hotels")


class Restaurant(Base):
    __tablename__ = "restaurants"

    destination_id: Mapped[str] = mapped_column(String(36), ForeignKey("destinations.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    cuisine_type: Mapped[List[str]] = mapped_column(JSON, default=list)  # ["seafood", "bangladeshi", "continental"]
    price_tier: Mapped[str] = mapped_column(String(10), default="$$")  # $, $$, $$$, $$$$
    average_cost_per_person: Mapped[float] = mapped_column(Float, default=600.0)
    currency: Mapped[str] = mapped_column(String(10), default="BDT")
    rating: Mapped[float] = mapped_column(Float, default=4.5)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    opening_hours: Mapped[Optional[str]] = mapped_column(String(255), default="10:00 - 23:00")
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Relationships
    destination: Mapped["Destination"] = relationship("Destination", back_populates="restaurants")
