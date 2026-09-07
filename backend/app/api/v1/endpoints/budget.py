from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.budget import Budget, Expense
from app.models.trip import Trip
from app.schemas.budget import (
    BudgetSummary,
    BudgetCreate,
    BudgetUpdate,
    ExpenseCreate,
    ExpenseResponse,
)
from app.services.budget_service import budget_service
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/trips/{trip_id}", response_model=BudgetSummary)
async def get_trip_budget(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full trip budget summary with category breakdowns and alerts."""
    try:
        return await budget_service.get_trip_budget_summary(trip_id=trip_id, db=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/trips/{trip_id}", response_model=BudgetSummary)
async def update_budget(
    trip_id: str,
    budget_in: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update custom category allocations for a trip budget."""
    stmt = select(Budget).where(Budget.trip_id == trip_id)
    res = await db.execute(stmt)
    budget = res.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found.")

    update_dict = budget_in.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(budget, k, v)

    db.add(budget)
    await db.commit()
    return await budget_service.get_trip_budget_summary(trip_id=trip_id, db=db)


@router.post("/trips/{trip_id}/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def add_expense(
    trip_id: str,
    exp_in: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log an actual expense against the trip budget."""
    stmt = select(Budget).where(Budget.trip_id == trip_id)
    res = await db.execute(stmt)
    budget = res.scalar_one_or_none()

    if not budget:
        # Create budget first
        trip_stmt = select(Trip).where(Trip.id == trip_id)
        trip_res = await db.execute(trip_stmt)
        trip = trip_res.scalar_one_or_none()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found.")
        splits = budget_service.calculate_recommended_budget_split(trip.total_budget)
        budget = Budget(trip_id=trip_id, total_budget=trip.total_budget, currency=trip.currency, **splits)
        db.add(budget)
        await db.flush()

    expense = Expense(
        budget_id=budget.id,
        category=exp_in.category,
        title=exp_in.title,
        amount=exp_in.amount,
        currency=exp_in.currency,
        expense_date=exp_in.expense_date or date.today(),
        payment_method=exp_in.payment_method,
        receipt_url=exp_in.receipt_url,
        notes=exp_in.notes,
    )
    db.add(expense)

    # Update trip actual cost
    trip_stmt = select(Trip).where(Trip.id == trip_id)
    trip_res = await db.execute(trip_stmt)
    trip = trip_res.scalar_one_or_none()
    if trip:
        trip.actual_cost += exp_in.amount
        db.add(trip)

    await db.commit()
    await db.refresh(expense)
    return expense


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an expense item."""
    stmt = select(Expense).where(Expense.id == expense_id)
    res = await db.execute(stmt)
    exp = res.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found.")
    await db.delete(exp)
    await db.commit()
