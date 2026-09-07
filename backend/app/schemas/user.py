from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class UserPreferenceSchema(BaseModel):
    preferred_budget_level: str = "moderate"
    travel_style: List[str] = ["beach", "relaxation", "nature"]
    dietary_restrictions: List[str] = ["halal"]
    preferred_transport: List[str] = ["flight", "car"]
    hotel_preferences: List[str] = ["resort", "hotel"]
    preferred_currency: str = "BDT"
    pace_preference: str = "moderate"
    interests: List[str] = ["photography", "beach", "food"]
    notes: Optional[str] = None


class UserPreferenceUpdate(BaseModel):
    preferred_budget_level: Optional[str] = None
    travel_style: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    preferred_transport: Optional[List[str]] = None
    hotel_preferences: Optional[List[str]] = None
    preferred_currency: Optional[str] = None
    pace_preference: Optional[str] = None
    interests: Optional[List[str]] = None
    notes: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    phone_number: Optional[str] = None
    home_country: Optional[str] = "Bangladesh"
    home_currency: str = "BDT"
    created_at: datetime
    preference: Optional[UserPreferenceSchema] = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    home_country: Optional[str] = None
    home_currency: Optional[str] = None
