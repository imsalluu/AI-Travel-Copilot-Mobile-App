from datetime import date, datetime
from typing import Optional, List, Dict
from pydantic import BaseModel


class ExpenseCreate(BaseModel):
    category: str = "food"  # transport, hotel, food, activity, shopping, misc
    title: str
    amount: float
    currency: str = "BDT"
    expense_date: Optional[date] = None
    payment_method: Optional[str] = "cash"
    receipt_url: Optional[str] = None
    notes: Optional[str] = None


class ExpenseResponse(ExpenseCreate):
    id: str
    budget_id: str
    expense_date: date
    created_at: datetime

    model_config = {"from_attributes": True}


class BudgetCreate(BaseModel):
    trip_id: str
    total_budget: float
    currency: str = "BDT"
    transport_budget: float = 0.0
    hotel_budget: float = 0.0
    food_budget: float = 0.0
    activity_budget: float = 0.0
    shopping_budget: float = 0.0
    misc_budget: float = 0.0
    notes: Optional[str] = None


class BudgetUpdate(BaseModel):
    total_budget: Optional[float] = None
    transport_budget: Optional[float] = None
    hotel_budget: Optional[float] = None
    food_budget: Optional[float] = None
    activity_budget: Optional[float] = None
    shopping_budget: Optional[float] = None
    misc_budget: Optional[float] = None
    notes: Optional[str] = None


class CategoryBreakdown(BaseModel):
    category: str
    budgeted: float
    spent: float
    remaining: float
    percentage_used: float


class BudgetSummary(BaseModel):
    trip_id: str
    total_budget: float
    total_spent: float
    remaining_budget: float
    currency: str = "BDT"
    daily_average: float
    days_count: int
    is_over_budget: bool
    status_warning: Optional[str] = None
    category_breakdowns: List[CategoryBreakdown] = []
    expenses: List[ExpenseResponse] = []
