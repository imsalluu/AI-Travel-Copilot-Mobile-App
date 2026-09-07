from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.trip import Trip, SavedPlace
from app.schemas.trip import (
    TripCreate,
    TripUpdate,
    TripResponse,
    SavedPlaceCreate,
    SavedPlaceResponse,
)
from app.services.trip_service import trip_service
from app.api.deps import get_current_user

router = APIRouter()


@router.get("", response_model=List[TripResponse])
async def list_trips(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all trips belonging to the authenticated user."""
    return await trip_service.get_user_trips(current_user.id, db, status_filter)


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    trip_in: TripCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new trip."""
    return await trip_service.create_trip(trip_in, current_user.id, db)


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get trip details by ID with days and activities."""
    trip = await trip_service.get_trip_by_id(trip_id, current_user.id, db)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")
    return trip


@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: str,
    trip_update: TripUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update trip properties (title, dates, budget, favorite status, etc.)."""
    trip = await trip_service.get_trip_by_id(trip_id, current_user.id, db)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")

    update_dict = trip_update.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(trip, field, value)

    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a trip and associated days/activities."""
    trip = await trip_service.get_trip_by_id(trip_id, current_user.id, db)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")
    await db.delete(trip)
    await db.commit()


@router.post("/{trip_id}/duplicate", response_model=TripResponse)
async def duplicate_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clone an existing trip with all its days and activities."""
    return await trip_service.duplicate_trip(trip_id, current_user.id, db)


# Saved Places endpoints
@router.get("/saved-places/all", response_model=List[SavedPlaceResponse])
async def list_saved_places(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all bookmarked places by current user."""
    stmt = select(SavedPlace).where(SavedPlace.user_id == current_user.id)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/saved-places", response_model=SavedPlaceResponse, status_code=status.HTTP_201_CREATED)
async def save_place(
    place_in: SavedPlaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save/bookmark a place."""
    saved = SavedPlace(
        user_id=current_user.id,
        name=place_in.name,
        category=place_in.category,
        destination=place_in.destination,
        latitude=place_in.latitude,
        longitude=place_in.longitude,
        notes=place_in.notes,
        image_url=place_in.image_url,
    )
    db.add(saved)
    await db.commit()
    await db.refresh(saved)
    return saved
