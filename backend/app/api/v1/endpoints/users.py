from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User, UserPreference, AuditLog
from app.schemas.user import UserResponse, UserUpdate, UserPreferenceSchema, UserPreferenceUpdate
from app.api.deps import get_current_user

router = APIRouter()


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile information."""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    if user_update.phone_number is not None:
        current_user.phone_number = user_update.phone_number
    if user_update.home_country is not None:
        current_user.home_country = user_update.home_country
    if user_update.home_currency is not None:
        current_user.home_currency = user_update.home_currency

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    stmt = select(UserPreference).where(UserPreference.user_id == current_user.id)
    res = await db.execute(stmt)
    current_user.preference = res.scalar_one_or_none()
    return current_user


@router.get("/me/preferences", response_model=UserPreferenceSchema)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user travel preferences."""
    stmt = select(UserPreference).where(UserPreference.user_id == current_user.id)
    res = await db.execute(stmt)
    pref = res.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)
        await db.commit()
        await db.refresh(pref)
    return pref


@router.put("/me/preferences", response_model=UserPreferenceSchema)
async def update_preferences(
    pref_update: UserPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user travel preferences (budget style, diet, transport, interests)."""
    stmt = select(UserPreference).where(UserPreference.user_id == current_user.id)
    res = await db.execute(stmt)
    pref = res.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)

    if pref_update.preferred_budget_level is not None:
        pref.preferred_budget_level = pref_update.preferred_budget_level
    if pref_update.travel_style is not None:
        pref.travel_style = pref_update.travel_style
    if pref_update.dietary_restrictions is not None:
        pref.dietary_restrictions = pref_update.dietary_restrictions
    if pref_update.preferred_transport is not None:
        pref.preferred_transport = pref_update.preferred_transport
    if pref_update.hotel_preferences is not None:
        pref.hotel_preferences = pref_update.hotel_preferences
    if pref_update.preferred_currency is not None:
        pref.preferred_currency = pref_update.preferred_currency
    if pref_update.pace_preference is not None:
        pref.pace_preference = pref_update.pace_preference
    if pref_update.interests is not None:
        pref.interests = pref_update.interests
    if pref_update.notes is not None:
        pref.notes = pref_update.notes

    db.add(pref)
    await db.commit()
    await db.refresh(pref)
    return pref
