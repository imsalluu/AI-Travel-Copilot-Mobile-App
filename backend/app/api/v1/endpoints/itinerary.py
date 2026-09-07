from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.trip import Activity, TripDay, Trip
from app.schemas.trip import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    TripDayResponse,
    TripResponse,
)
from app.schemas.itinerary import (
    ActivityReorderRequest,
    ActivityMoveRequest,
    StructuredItineraryPlan,
)
from app.services.trip_service import trip_service
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/trips/{trip_id}/days/{day_id}/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def add_activity(
    trip_id: str,
    day_id: str,
    act_in: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a new activity to a day's timeline."""
    try:
        activity = await trip_service.add_activity_to_day(
            trip_id=trip_id,
            day_id=day_id,
            act_in=act_in,
            user_id=current_user.id,
            db=db,
        )
        return activity
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/activities/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: str,
    act_update: ActivityUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update details or completion status of an activity."""
    stmt = select(Activity).where(Activity.id == activity_id)
    res = await db.execute(stmt)
    activity = res.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found.")

    update_dict = act_update.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(activity, field, val)

    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an activity from an itinerary day."""
    stmt = select(Activity).where(Activity.id == activity_id)
    res = await db.execute(stmt)
    activity = res.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found.")

    await db.delete(activity)
    await db.commit()


@router.post("/reorder", status_code=status.HTTP_200_OK)
async def reorder_activities(
    payload: ActivityReorderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reorder activity sequence in a day after drag-and-drop."""
    success = await trip_service.reorder_activities(
        day_id=payload.day_id,
        activity_ids=payload.activity_ids,
        user_id=current_user.id,
        db=db,
    )
    return {"status": "success", "reordered": success}


@router.post("/move", status_code=status.HTTP_200_OK)
async def move_activity(
    payload: ActivityMoveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Move an activity from one day to another day."""
    success = await trip_service.move_activity(
        activity_id=payload.activity_id,
        source_day_id=payload.source_day_id,
        target_day_id=payload.target_day_id,
        new_order_index=payload.new_order_index,
        db=db,
    )
    if not success:
        raise HTTPException(status_code=400, detail="Unable to move activity.")
    return {"status": "success", "moved": True}
