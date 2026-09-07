from typing import Optional, List
from pydantic import BaseModel, Field


class ActivityPlan(BaseModel):
    title: str = Field(..., description="Activity title, e.g. 'Laboni Beach Sunset & Photography'")
    description: Optional[str] = Field(None, description="Detailed tips, advice, or description")
    category: str = Field("attraction", description="attraction, meal, hotel, transport, leisure, shopping")
    location_name: str = Field(..., description="Specific name of the venue/spot")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_time: str = Field("09:00", description="HH:MM format, 24-hour")
    end_time: str = Field("10:30", description="HH:MM format, 24-hour")
    duration_minutes: int = Field(90, description="Duration in minutes")
    estimated_cost: float = Field(0.0, description="Estimated cost in local currency")
    currency: str = Field("BDT", description="Currency code")
    travel_time_from_previous_minutes: int = Field(0, description="Travel time from previous activity")
    travel_mode: str = Field("drive", description="walk, drive, transit, boat")
    notes: Optional[str] = None
    is_indoor: bool = False


class ItineraryDayPlan(BaseModel):
    day_number: int = Field(..., description="Day index starting at 1")
    date_str: Optional[str] = None  # YYYY-MM-DD
    title: str = Field(..., description="E.g., 'Arrival & Coastal Sunset Experience'")
    theme: Optional[str] = Field(None, description="E.g., 'Coastal Exploration & Seafood'")
    notes: Optional[str] = None
    estimated_day_cost: float = Field(0.0, description="Total estimated cost for this day")
    activities: List[ActivityPlan] = Field(default_factory=list)


class StructuredItineraryPlan(BaseModel):
    title: str = Field(..., description="Trip title, e.g. '3-Day Tropical Cox\\'s Bazar Escape'")
    destination: str = Field(..., description="Target destination")
    duration_days: int = Field(..., description="Number of days")
    total_budget: float = Field(..., description="Target budget")
    estimated_cost: float = Field(..., description="Calculated total cost")
    currency: str = Field("BDT", description="Currency code")
    travel_style: str = Field("balanced", description="luxury, budget, adventure, relaxation, family")
    description: Optional[str] = None
    weather_summary: Optional[dict] = None
    packing_suggestions: List[str] = Field(default_factory=list)
    travel_tips: List[str] = Field(default_factory=list)
    days: List[ItineraryDayPlan] = Field(default_factory=list)


class ConversationalModificationRequest(BaseModel):
    trip_id: str
    user_instruction: str = Field(..., description="E.g. 'Make day 2 less busy', 'Add sunset boat ride'")
    day_number: Optional[int] = None


class ActivityReorderRequest(BaseModel):
    day_id: str
    activity_ids: List[str] = Field(..., description="Ordered list of activity IDs for the day")


class ActivityMoveRequest(BaseModel):
    activity_id: str
    source_day_id: str
    target_day_id: str
    new_order_index: int = 0
