from typing import Optional, List
from datetime import date
from sqlalchemy import String, Float, JSON, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    trip_id: Mapped[str] = mapped_column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), unique=True, index=True)
    total_budget: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="BDT")
    
    # Category limits
    transport_budget: Mapped[float] = mapped_column(Float, default=0.0)
    hotel_budget: Mapped[float] = mapped_column(Float, default=0.0)
    food_budget: Mapped[float] = mapped_column(Float, default=0.0)
    activity_budget: Mapped[float] = mapped_column(Float, default=0.0)
    shopping_budget: Mapped[float] = mapped_column(Float, default=0.0)
    misc_budget: Mapped[float] = mapped_column(Float, default=0.0)
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="budget_record")
    expenses: Mapped[List["Expense"]] = relationship("Expense", back_populates="budget", cascade="all, delete-orphan")


class Expense(Base):
    __tablename__ = "expenses"

    budget_id: Mapped[str] = mapped_column(String(36), ForeignKey("budgets.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(64), default="food")  # transport, hotel, food, activity, shopping, misc
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="BDT")
    expense_date: Mapped[date] = mapped_column(Date, default=date.today)
    payment_method: Mapped[Optional[str]] = mapped_column(String(64), default="cash")  # cash, card, mobile_banking
    receipt_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    budget: Mapped["Budget"] = relationship("Budget", back_populates="expenses")
