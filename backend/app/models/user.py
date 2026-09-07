from typing import Optional, List
from sqlalchemy import String, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    home_country: Mapped[Optional[str]] = mapped_column(String(100), default="Bangladesh")
    home_currency: Mapped[str] = mapped_column(String(10), default="BDT")

    # Relationships
    preference: Mapped[Optional["UserPreference"]] = relationship(
        "UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    trips: Mapped[List["Trip"]] = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    saved_places: Mapped[List["SavedPlace"]] = relationship("SavedPlace", back_populates="user", cascade="all, delete-orphan")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    preferred_budget_level: Mapped[str] = mapped_column(String(32), default="moderate")  # budget, moderate, luxury
    travel_style: Mapped[List[str]] = mapped_column(JSON, default=list)  # ["adventure", "beach", "cultural", "relaxation"]
    dietary_restrictions: Mapped[List[str]] = mapped_column(JSON, default=list)  # ["halal", "vegetarian", "gluten-free"]
    preferred_transport: Mapped[List[str]] = mapped_column(JSON, default=list)  # ["flight", "train", "car", "boat"]
    hotel_preferences: Mapped[List[str]] = mapped_column(JSON, default=list)  # ["resort", "boutique", "hostel", "4-star"]
    preferred_currency: Mapped[str] = mapped_column(String(10), default="BDT")
    pace_preference: Mapped[str] = mapped_column(String(32), default="moderate")  # relaxed, moderate, fast_paced
    interests: Mapped[List[str]] = mapped_column(JSON, default=list)  # ["photography", "nature", "history", "food", "shopping"]
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="preference")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
