from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.budget import Budget, Expense
from app.models.trip import Trip
from app.schemas.budget import BudgetSummary, CategoryBreakdown, ExpenseResponse


class BudgetService:
    """Service for calculating, tracking, and optimizing trip finances and category expenditures."""

    @staticmethod
    def calculate_recommended_budget_split(total_budget: float) -> Dict[str, float]:
        """Produce standard travel budget allocation across essential categories."""
        return {
            "transport_budget": round(total_budget * 0.25, 2),
            "hotel_budget": round(total_budget * 0.35, 2),
            "food_budget": round(total_budget * 0.20, 2),
            "activity_budget": round(total_budget * 0.12, 2),
            "shopping_budget": round(total_budget * 0.05, 2),
            "misc_budget": round(total_budget * 0.03, 2),
        }

    @classmethod
    async def get_trip_budget_summary(cls, trip_id: str, db: AsyncSession) -> BudgetSummary:
        """Fetch or calculate full budget summary including expense rollups and warning alerts."""
        # Fetch Trip
        trip_stmt = select(Trip).where(Trip.id == trip_id)
        res = await db.execute(trip_stmt)
        trip = res.scalar_one_or_none()

        if not trip:
            raise ValueError(f"Trip with ID {trip_id} not found.")

        # Fetch Budget record
        b_stmt = select(Budget).where(Budget.trip_id == trip_id)
        b_res = await db.execute(b_stmt)
        budget = b_res.scalar_one_or_none()

        if not budget:
            # Auto-create budget initialized from trip total_budget
            splits = cls.calculate_recommended_budget_split(trip.total_budget)
            budget = Budget(
                trip_id=trip.id,
                total_budget=trip.total_budget,
                currency=trip.currency,
                **splits,
            )
            db.add(budget)
            await db.commit()
            await db.refresh(budget)

        # Fetch Expenses
        exp_stmt = select(Expense).where(Expense.budget_id == budget.id).order_by(Expense.expense_date.desc())
        exp_res = await db.execute(exp_stmt)
        expenses = exp_res.scalars().all()

        total_spent = sum(e.amount for e in expenses)
        remaining = budget.total_budget - total_spent
        days_count = max(trip.duration_days, 1)
        daily_avg = total_spent / days_count

        # Category rollups
        cat_map = {
            "transport": {"budgeted": budget.transport_budget, "spent": 0.0},
            "hotel": {"budgeted": budget.hotel_budget, "spent": 0.0},
            "food": {"budgeted": budget.food_budget, "spent": 0.0},
            "activity": {"budgeted": budget.activity_budget, "spent": 0.0},
            "shopping": {"budgeted": budget.shopping_budget, "spent": 0.0},
            "misc": {"budgeted": budget.misc_budget, "spent": 0.0},
        }

        for e in expenses:
            cat = e.category.lower()
            if cat in cat_map:
                cat_map[cat]["spent"] += e.amount
            else:
                cat_map["misc"]["spent"] += e.amount

        category_breakdowns = []
        for cat_name, data in cat_map.items():
            b_val = data["budgeted"]
            s_val = data["spent"]
            rem = b_val - s_val
            pct = round((s_val / b_val * 100.0) if b_val > 0 else 0.0, 1)
            category_breakdowns.append(
                CategoryBreakdown(
                    category=cat_name,
                    budgeted=b_val,
                    spent=s_val,
                    remaining=rem,
                    percentage_used=pct,
                )
            )

        is_over = total_spent > budget.total_budget and budget.total_budget > 0
        warning = None
        if is_over:
            warning = f"Current spending exceeds total budget by {total_spent - budget.total_budget:.2f} {budget.currency}. Consider opting for budget dining or free beach/nature activities."
        elif remaining < (budget.total_budget * 0.15) and budget.total_budget > 0:
            warning = "Less than 15% budget remaining. Recommend reserving remaining funds for return transit."

        # Convert expenses to response schemas
        exp_schemas = [
            ExpenseResponse(
                id=e.id,
                budget_id=e.budget_id,
                category=e.category,
                title=e.title,
                amount=e.amount,
                currency=e.currency,
                expense_date=e.expense_date,
                payment_method=e.payment_method,
                receipt_url=e.receipt_url,
                notes=e.notes,
                created_at=e.created_at,
            )
            for e in expenses
        ]

        return BudgetSummary(
            trip_id=trip_id,
            total_budget=budget.total_budget,
            total_spent=round(total_spent, 2),
            remaining_budget=round(remaining, 2),
            currency=budget.currency,
            daily_average=round(daily_avg, 2),
            days_count=days_count,
            is_over_budget=is_over,
            status_warning=warning,
            category_breakdowns=category_breakdowns,
            expenses=exp_schemas,
        )


budget_service = BudgetService()
