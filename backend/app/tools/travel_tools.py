from typing import List, Dict, Any, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.destination import Destination, Place, Hotel, Restaurant
from app.models.trip import Trip, TripDay, Activity
from app.services.map_service import map_service
from app.services.weather_service import weather_service
from app.services.budget_service import budget_service
from app.rag.vector_store import vector_store
from app.tools.base import BaseTravelTool


class TravelToolSuite:
    """Complete suite of 14 travel tools used by the LangGraph Travel Agent."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_places(self, destination: str, category: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search attractions and scenic points in a destination."""
        stmt = select(Place).join(Destination).where(Destination.name.ilike(f"%{destination}%"))
        if category:
            stmt = stmt.where(Place.category == category)
        res = await self.db.execute(stmt)
        places = res.scalars().all()[:max_results]
        return [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "description": p.description,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "estimated_cost": p.estimated_cost,
                "typical_duration_minutes": p.typical_duration_minutes,
                "rating": p.rating,
                "is_indoor": p.is_indoor,
            }
            for p in places
        ]

    async def get_place_details(self, place_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information, address, operating hours, and cost for a specific place."""
        stmt = select(Place).where(Place.name.ilike(f"%{place_name}%"))
        res = await self.db.execute(stmt)
        p = res.scalar_one_or_none()
        if not p:
            return {"error": f"Place {place_name} not found"}
        return {
            "name": p.name,
            "category": p.category,
            "description": p.description,
            "address": p.address,
            "opening_hours": p.opening_hours,
            "estimated_cost": p.estimated_cost,
            "rating": p.rating,
            "is_indoor": p.is_indoor,
        }

    async def search_hotels(self, destination: str, max_price: Optional[float] = None) -> List[Dict[str, Any]]:
        """Search hotels and resorts in a destination matching budget criteria."""
        stmt = select(Hotel).join(Destination).where(Destination.name.ilike(f"%{destination}%"))
        if max_price:
            stmt = stmt.where(Hotel.price_per_night <= max_price)
        res = await self.db.execute(stmt)
        hotels = res.scalars().all()
        return [
            {
                "name": h.name,
                "category": h.category,
                "star_rating": h.star_rating,
                "price_per_night": h.price_per_night,
                "amenities": h.amenities,
                "latitude": h.latitude,
                "longitude": h.longitude,
            }
            for h in hotels
        ]

    async def search_restaurants(self, destination: str, cuisine: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find popular restaurants and local eateries in a destination."""
        stmt = select(Restaurant).join(Destination).where(Destination.name.ilike(f"%{destination}%"))
        res = await self.db.execute(stmt)
        restaurants = res.scalars().all()
        return [
            {
                "name": r.name,
                "cuisine_type": r.cuisine_type,
                "price_tier": r.price_tier,
                "average_cost_per_person": r.average_cost_per_person,
                "description": r.description,
            }
            for r in restaurants
        ]

    async def get_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> Dict[str, Any]:
        """Calculate road/straight-line distance between two geographic coordinates."""
        dist = map_service.calculate_haversine_distance_km(lat1, lon1, lat2, lon2)
        return {"distance_km": dist}

    async def get_travel_time(self, lat1: float, lon1: float, lat2: float, lon2: float, mode: str = "drive") -> Dict[str, Any]:
        """Estimate travel duration between two coordinates based on transport mode."""
        time_mins = map_service.estimate_travel_time_minutes(lat1, lon1, lat2, lon2, mode)
        return {"travel_time_minutes": time_mins, "mode": mode}

    async def get_weather(self, destination: str, duration_days: int = 3) -> Dict[str, Any]:
        """Check weather conditions, rain forecast, and outdoor suitability."""
        return await weather_service.get_weather_for_destination(destination, duration_days=duration_days)

    async def calculate_trip_budget(self, total_budget: float, duration_days: int) -> Dict[str, Any]:
        """Calculate category-wise budget allocations and daily allowances."""
        splits = budget_service.calculate_recommended_budget_split(total_budget)
        daily_allowance = total_budget / max(duration_days, 1)
        return {
            "total_budget": total_budget,
            "daily_allowance": round(daily_allowance, 2),
            "allocations": splits,
        }

    async def search_destination_knowledge(self, query: str, destination: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search grounded travel rules, safety advisories, and local tips via RAG."""
        return await vector_store.search(query=query, destination=destination, top_k=3, db=self.db)

    async def get_currency_rate(self, from_currency: str = "USD", to_currency: str = "BDT") -> Dict[str, Any]:
        """Get exchange rates for multi-currency travel budgeting."""
        rates = {
            ("USD", "BDT"): 120.50,
            ("BDT", "USD"): 0.0083,
            ("EUR", "BDT"): 131.20,
            ("GBP", "BDT"): 154.00,
        }
        rate = rates.get((from_currency.upper(), to_currency.upper()), 1.0)
        return {"from": from_currency, "to": to_currency, "exchange_rate": rate}


def get_all_tool_definitions() -> List[Dict[str, Any]]:
    """Return JSON schemas for all agent tool calling capabilities."""
    return [
        {
            "name": "search_places",
            "description": "Search attractions, beaches, parks, viewpoints in a destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "Target destination city/area"},
                    "category": {"type": "string", "description": "beach, nature, museum, viewpoint"},
                },
                "required": ["destination"],
            },
        },
        {
            "name": "get_place_details",
            "description": "Get opening hours, ticket costs, and details for a named place.",
            "parameters": {
                "type": "object",
                "properties": {"place_name": {"type": "string"}},
                "required": ["place_name"],
            },
        },
        {
            "name": "search_hotels",
            "description": "Find hotels or resorts within a price budget.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "max_price": {"type": "number"},
                },
                "required": ["destination"],
            },
        },
        {
            "name": "search_restaurants",
            "description": "Find top-rated dining and local cuisine restaurants.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "cuisine": {"type": "string"},
                },
                "required": ["destination"],
            },
        },
        {
            "name": "get_weather",
            "description": "Get current weather condition and multi-day rain probability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "duration_days": {"type": "integer"},
                },
                "required": ["destination"],
            },
        },
        {
            "name": "calculate_trip_budget",
            "description": "Calculate category-wise split and daily limits for a total budget.",
            "parameters": {
                "type": "object",
                "properties": {
                    "total_budget": {"type": "number"},
                    "duration_days": {"type": "integer"},
                },
                "required": ["total_budget", "duration_days"],
            },
        },
        {
            "name": "search_destination_knowledge",
            "description": "Retrieve official safety guidelines, transport tips, and local cultural rules.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "destination": {"type": "string"},
                },
                "required": ["query"],
            },
        },
        {
            "name": "get_currency_rate",
            "description": "Get conversion exchange rate between currencies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {"type": "string"},
                    "to_currency": {"type": "string"},
                },
                "required": ["from_currency", "to_currency"],
            },
        },
    ]
