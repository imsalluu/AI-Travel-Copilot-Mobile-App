from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.itinerary import ActivityPlan, ItineraryDayPlan


class ActivityCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "attraction"
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_time: Optional[str] = "09:00"
    end_time: Optional[str] = "10:30"
    duration_minutes: int = 90
    estimated_cost: float = 0.0
    currency: str = "BDT"
    travel_time_from_previous_minutes: int = 0
    travel_mode: Optional[str] = "drive"
    notes: Optional[str] = None
    is_indoor: bool = False
    order_index: int = 0


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    estimated_cost: Optional[float] = None
    travel_time_from_previous_minutes: Optional[int] = None
    travel_mode: Optional[str] = None
    notes: Optional[str] = None
    is_indoor: Optional[bool] = None
    is_completed: Optional[bool] = None
    order_index: Optional[int] = None


class ActivityResponse(ActivityCreate):
    id: str
    trip_day_id: str
    is_completed: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class TripDayCreate(BaseModel):
    day_number: int
    date: date
    title: Optional[str] = None
    theme: Optional[str] = None
    notes: Optional[str] = None
    estimated_day_cost: float = 0.0


class TripDayResponse(BaseModel):
    id: str
    trip_id: str
    day_number: int
    date: date
    title: Optional[str] = None
    theme: Optional[str] = None
    notes: Optional[str] = None
    weather_forecast: Optional[dict] = None
    estimated_day_cost: float = 0.0
    activities: List[ActivityResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class TripCreate(BaseModel):
    title: str = Field(..., description="Trip title")
    destination: str = Field(..., description="Destination city/region")
    start_date: date
    end_date: date
    duration_days: Optional[int] = None
    travelers_count: int = 1
    total_budget: float = 0.0
    currency: str = "BDT"
    travel_style: Optional[str] = "moderate"
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    notes: Optional[str] = None


class TripUpdate(BaseModel):
    title: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    travelers_count: Optional[int] = None
    status: Optional[str] = None
    total_budget: Optional[float] = None
    currency: Optional[str] = None
    travel_style: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_favorite: Optional[bool] = None
    notes: Optional[str] = None


class TripResponse(BaseModel):
    id: str
    user_id: str
    title: str
    destination: str
    start_date: date
    end_date: date
    duration_days: int
    travelers_count: int
    status: str
    cover_image_url: Optional[str] = None
    description: Optional[str] = None
    travel_style: Optional[str] = None
    total_budget: float
    estimated_cost: float
    actual_cost: float
    currency: str
    is_favorite: bool
    notes: Optional[str] = None
    packing_list: List[str] = []
    weather_summary: Optional[dict] = None
    ai_summary: Optional[str] = None
    days: List[TripDayResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SavedPlaceCreate(BaseModel):
    name: str
    category: str = "place"
    destination: str
    latitude: float
    longitude: float
    notes: Optional[str] = None
    image_url: Optional[str] = None


class SavedPlaceResponse(SavedPlaceCreate):
    id: str
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
