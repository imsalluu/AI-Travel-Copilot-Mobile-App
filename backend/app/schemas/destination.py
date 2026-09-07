from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class PlaceBase(BaseModel):
    name: str
    category: str
    description: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    rating: float = 4.5
    reviews_count: int = 0
    typical_duration_minutes: int = 90
    estimated_cost: float = 0.0
    currency: str = "BDT"
    opening_hours: Optional[str] = "09:00 - 18:00"
    is_indoor: bool = False
    image_url: Optional[str] = None
    tags: List[str] = []


class PlaceResponse(PlaceBase):
    id: str
    destination_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HotelBase(BaseModel):
    name: str
    category: str = "hotel"
    star_rating: float = 4.0
    rating: float = 4.5
    description: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    price_per_night: float
    currency: str = "BDT"
    amenities: List[str] = []
    image_url: Optional[str] = None


class HotelResponse(HotelBase):
    id: str
    destination_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RestaurantBase(BaseModel):
    name: str
    cuisine_type: List[str] = []
    price_tier: str = "$$"
    average_cost_per_person: float = 600.0
    currency: str = "BDT"
    rating: float = 4.5
    description: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    opening_hours: Optional[str] = "10:00 - 23:00"
    image_url: Optional[str] = None


class RestaurantResponse(RestaurantBase):
    id: str
    destination_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DestinationBase(BaseModel):
    name: str
    country: str
    region: Optional[str] = None
    description: str
    latitude: float
    longitude: float
    best_time_to_visit: Optional[str] = None
    climate: Optional[str] = None
    currency: str = "BDT"
    average_daily_cost: float = 5000.0
    image_url: Optional[str] = None
    gallery: List[str] = []
    tags: List[str] = []
    safety_rating: float = 4.5


class DestinationResponse(DestinationBase):
    id: str
    created_at: datetime
    places: List[PlaceResponse] = []
    hotels: List[HotelResponse] = []
    restaurants: List[RestaurantResponse] = []

    model_config = {"from_attributes": True}
