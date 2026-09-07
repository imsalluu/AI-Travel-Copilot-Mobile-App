from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from app.models.trip import Trip, TripDay, Activity, SavedPlace, TripStatus
from app.models.budget import Budget
from app.schemas.trip import TripCreate, TripUpdate, ActivityCreate, ActivityUpdate
from app.schemas.itinerary import StructuredItineraryPlan, ActivityPlan, ItineraryDayPlan


class TripService:
    """Service handling Trip lifecycles, structured itinerary persistence, and timeline operations."""

    @classmethod
    async def get_user_trips(cls, user_id: str, db: AsyncSession, status: Optional[str] = None) -> List[Trip]:
        """Fetch all trips for a user with days and activities eagerly loaded."""
        stmt = (
            select(Trip)
            .where(Trip.user_id == user_id)
            .options(selectinload(Trip.days).selectinload(TripDay.activities))
            .order_by(Trip.created_at.desc())
        )
        if status:
            stmt = stmt.where(Trip.status == status)
        result = await db.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get_trip_by_id(cls, trip_id: str, user_id: str, db: AsyncSession) -> Optional[Trip]:
        """Fetch a specific trip by ID ensuring ownership."""
        stmt = (
            select(Trip)
            .where(Trip.id == trip_id, Trip.user_id == user_id)
            .options(selectinload(Trip.days).selectinload(TripDay.activities))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def create_trip(cls, trip_in: TripCreate, user_id: str, db: AsyncSession) -> Trip:
        """Create a new trip and initialize its empty day buckets."""
        duration = trip_in.duration_days or ((trip_in.end_date - trip_in.start_date).days + 1)
        if duration < 1:
            duration = 1

        trip = Trip(
            user_id=user_id,
            title=trip_in.title,
            destination=trip_in.destination,
            start_date=trip_in.start_date,
            end_date=trip_in.end_date,
            duration_days=duration,
            travelers_count=trip_in.travelers_count,
            status=TripStatus.PLANNED.value,
            total_budget=trip_in.total_budget,
            currency=trip_in.currency,
            travel_style=trip_in.travel_style,
            description=trip_in.description,
            cover_image_url=trip_in.cover_image_url or "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
            notes=trip_in.notes,
        )
        db.add(trip)
        await db.flush()

        # Generate day slots
        for day_idx in range(1, duration + 1):
            day_date = trip.start_date + timedelta(days=day_idx - 1)
            day = TripDay(
                trip_id=trip.id,
                day_number=day_idx,
                date=day_date,
                title=f"Day {day_idx}: Explore {trip.destination}",
            )
            db.add(day)

        await db.commit()
        return await cls.get_trip_by_id(trip.id, user_id, db)

    @classmethod
    async def save_structured_itinerary(
        cls,
        user_id: str,
        itinerary: StructuredItineraryPlan,
        start_date: Optional[date] = None,
        db: AsyncSession = None,
        existing_trip_id: Optional[str] = None
    ) -> Trip:
        """Persist a complete AI-generated structured itinerary to the database."""
        trip_start = start_date or date.today()
        trip_end = trip_start + timedelta(days=itinerary.duration_days - 1)

        if existing_trip_id:
            trip = await cls.get_trip_by_id(existing_trip_id, user_id, db)
            if not trip:
                raise ValueError(f"Trip {existing_trip_id} not found.")
            # Clear existing days and activities for fresh structured replacement
            for day in trip.days:
                await db.delete(day)
            await db.flush()
        else:
            trip = Trip(
                user_id=user_id,
                title=itinerary.title,
                destination=itinerary.destination,
                start_date=trip_start,
                end_date=trip_end,
                duration_days=itinerary.duration_days,
                travelers_count=1,
                status=TripStatus.PLANNED.value,
                total_budget=itinerary.total_budget,
                estimated_cost=itinerary.estimated_cost,
                currency=itinerary.currency,
                travel_style=itinerary.travel_style,
                description=itinerary.description,
                packing_list=itinerary.packing_suggestions,
                weather_summary=itinerary.weather_summary,
                ai_summary="\n".join(itinerary.travel_tips),
                cover_image_url="https://images.unsplash.com/photo-1544735716-392fe2489ffa",
            )
            db.add(trip)
            await db.flush()

        # Populate Days & Activities
        total_calculated_cost = 0.0
        for day_plan in itinerary.days:
            day_date = trip_start + timedelta(days=day_plan.day_number - 1)
            trip_day = TripDay(
                trip_id=trip.id,
                day_number=day_plan.day_number,
                date=day_date,
                title=day_plan.title,
                theme=day_plan.theme,
                notes=day_plan.notes,
                estimated_day_cost=day_plan.estimated_day_cost,
            )
            db.add(trip_day)
            await db.flush()

            for order_idx, act in enumerate(day_plan.activities):
                activity = Activity(
                    trip_day_id=trip_day.id,
                    order_index=order_idx,
                    title=act.title,
                    description=act.description,
                    category=act.category,
                    location_name=act.location_name,
                    latitude=act.latitude,
                    longitude=act.longitude,
                    start_time=act.start_time,
                    end_time=act.end_time,
                    duration_minutes=act.duration_minutes,
                    estimated_cost=act.estimated_cost,
                    currency=act.currency,
                    travel_time_from_previous_minutes=act.travel_time_from_previous_minutes,
                    travel_mode=act.travel_mode,
                    notes=act.notes,
                    is_indoor=act.is_indoor,
                )
                db.add(activity)
                total_calculated_cost += act.estimated_cost

        trip.estimated_cost = total_calculated_cost if total_calculated_cost > 0 else itinerary.estimated_cost
        await db.commit()
        return await cls.get_trip_by_id(trip.id, user_id, db)

    @classmethod
    async def add_activity_to_day(
        cls,
        trip_id: str,
        day_id: str,
        act_in: ActivityCreate,
        user_id: str,
        db: AsyncSession
    ) -> Activity:
        """Add an activity to a specific day in a trip."""
        trip = await cls.get_trip_by_id(trip_id, user_id, db)
        if not trip:
            raise ValueError("Trip not found or unauthorized.")

        # Find current highest order index in day
        stmt = select(Activity).where(Activity.trip_day_id == day_id).order_by(Activity.order_index.desc())
        res = await db.execute(stmt)
        existing = res.scalars().all()
        next_order = len(existing)

        activity = Activity(
            trip_day_id=day_id,
            order_index=next_order,
            title=act_in.title,
            description=act_in.description,
            category=act_in.category,
            location_name=act_in.location_name,
            latitude=act_in.latitude,
            longitude=act_in.longitude,
            start_time=act_in.start_time,
            end_time=act_in.end_time,
            duration_minutes=act_in.duration_minutes,
            estimated_cost=act_in.estimated_cost,
            currency=act_in.currency,
            travel_time_from_previous_minutes=act_in.travel_time_from_previous_minutes,
            travel_mode=act_in.travel_mode,
            notes=act_in.notes,
            is_indoor=act_in.is_indoor,
        )
        db.add(activity)
        # Update trip estimated cost
        trip.estimated_cost += act_in.estimated_cost
        await db.commit()
        await db.refresh(activity)
        return activity

    @classmethod
    async def reorder_activities(
        cls,
        day_id: str,
        activity_ids: List[str],
        user_id: str,
        db: AsyncSession
    ) -> bool:
        """Update sequential order indices for activities within a day."""
        for new_idx, act_id in enumerate(activity_ids):
            stmt = (
                update(Activity)
                .where(Activity.id == act_id, Activity.trip_day_id == day_id)
                .values(order_index=new_idx)
            )
            await db.execute(stmt)
        await db.commit()
        return True

    @classmethod
    async def move_activity(
        cls,
        activity_id: str,
        source_day_id: str,
        target_day_id: str,
        new_order_index: int,
        db: AsyncSession
    ) -> bool:
        """Move an activity from one trip day to another."""
        stmt = select(Activity).where(Activity.id == activity_id, Activity.trip_day_id == source_day_id)
        res = await db.execute(stmt)
        act = res.scalar_one_or_none()
        if not act:
            return False

        act.trip_day_id = target_day_id
        act.order_index = new_order_index
        db.add(act)
        await db.commit()
        return True

    @classmethod
    async def duplicate_trip(cls, trip_id: str, user_id: str, db: AsyncSession) -> Trip:
        """Duplicate an existing trip including all days and activities."""
        orig = await cls.get_trip_by_id(trip_id, user_id, db)
        if not orig:
            raise ValueError("Original trip not found.")

        new_trip = Trip(
            user_id=user_id,
            title=f"Copy of {orig.title}",
            destination=orig.destination,
            start_date=orig.start_date,
            end_date=orig.end_date,
            duration_days=orig.duration_days,
            travelers_count=orig.travelers_count,
            status=TripStatus.PLANNED.value,
            total_budget=orig.total_budget,
            estimated_cost=orig.estimated_cost,
            currency=orig.currency,
            travel_style=orig.travel_style,
            description=orig.description,
            cover_image_url=orig.cover_image_url,
            packing_list=orig.packing_list,
            weather_summary=orig.weather_summary,
            ai_summary=orig.ai_summary,
        )
        db.add(new_trip)
        await db.flush()

        for day in orig.days:
            new_day = TripDay(
                trip_id=new_trip.id,
                day_number=day.day_number,
                date=day.date,
                title=day.title,
                theme=day.theme,
                notes=day.notes,
                estimated_day_cost=day.estimated_day_cost,
            )
            db.add(new_day)
            await db.flush()

            for act in day.activities:
                new_act = Activity(
                    trip_day_id=new_day.id,
                    order_index=act.order_index,
                    title=act.title,
                    description=act.description,
                    category=act.category,
                    location_name=act.location_name,
                    latitude=act.latitude,
                    longitude=act.longitude,
                    start_time=act.start_time,
                    end_time=act.end_time,
                    duration_minutes=act.duration_minutes,
                    estimated_cost=act.estimated_cost,
                    currency=act.currency,
                    travel_time_from_previous_minutes=act.travel_time_from_previous_minutes,
                    travel_mode=act.travel_mode,
                    notes=act.notes,
                    is_indoor=act.is_indoor,
                )
                db.add(new_act)

        await db.commit()
        return await cls.get_trip_by_id(new_trip.id, user_id, db)


trip_service = TripService()
