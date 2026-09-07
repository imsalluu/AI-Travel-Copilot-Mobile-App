from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.destination import Destination, Place, Hotel, Restaurant
from app.schemas.destination import (
    DestinationResponse,
    PlaceResponse,
    HotelResponse,
    RestaurantResponse,
)

router = APIRouter()


@router.get("", response_model=List[DestinationResponse])
async def list_destinations(
    query: Optional[str] = Query(None, description="Search destination name or tags"),
    db: AsyncSession = Depends(get_db),
):
    """List curated travel destinations with attractions, hotels, and dining."""
    stmt = (
        select(Destination)
        .options(
            selectinload(Destination.places),
            selectinload(Destination.hotels),
            selectinload(Destination.restaurants),
        )
    )
    if query:
        stmt = stmt.where(Destination.name.ilike(f"%{query}%"))
    res = await db.execute(stmt)
    destinations = res.scalars().all()

    if not destinations:
        # Seed default destinations if table is empty
        await _seed_default_destinations(db)
        res = await db.execute(stmt)
        destinations = res.scalars().all()

    return destinations


@router.get("/{destination_id}", response_model=DestinationResponse)
async def get_destination(destination_id: str, db: AsyncSession = Depends(get_db)):
    """Get single destination details."""
    stmt = (
        select(Destination)
        .where(Destination.id == destination_id)
        .options(
            selectinload(Destination.places),
            selectinload(Destination.hotels),
            selectinload(Destination.restaurants),
        )
    )
    res = await db.execute(stmt)
    dest = res.scalar_one_or_none()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found.")
    return dest


@router.get("/{destination_id}/places", response_model=List[PlaceResponse])
async def list_destination_places(
    destination_id: str,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List places and attractions for a destination."""
    stmt = select(Place).where(Place.destination_id == destination_id)
    if category:
        stmt = stmt.where(Place.category == category)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/{destination_id}/hotels", response_model=List[HotelResponse])
async def list_destination_hotels(destination_id: str, db: AsyncSession = Depends(get_db)):
    """List hotels and resorts for a destination."""
    stmt = select(Hotel).where(Hotel.destination_id == destination_id)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/{destination_id}/restaurants", response_model=List[RestaurantResponse])
async def list_destination_restaurants(destination_id: str, db: AsyncSession = Depends(get_db)):
    """List restaurants and eateries for a destination."""
    stmt = select(Restaurant).where(Restaurant.destination_id == destination_id)
    res = await db.execute(stmt)
    return res.scalars().all()


async def _seed_default_destinations(db: AsyncSession):
    """Seed high-quality destination data (Cox's Bazar, Sylhet, Sajek Valley)."""
    # 1. Cox's Bazar
    cb = Destination(
        name="Cox's Bazar",
        country="Bangladesh",
        region="Chittagong Division",
        description="The world's longest unbroken natural sea beach, spanning over 120 km of golden sand, scenic hills, marine drive, and fresh seafood.",
        latitude=21.4272,
        longitude=92.0058,
        best_time_to_visit="November to March",
        climate="Tropical monsoon",
        currency="BDT",
        average_daily_cost=5500.0,
        image_url="https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
        tags=["beach", "sunset", "marine drive", "seafood", "surfing"],
        safety_rating=4.7,
    )
    db.add(cb)
    await db.flush()

    cb_places = [
        Place(
            destination_id=cb.id,
            name="Laboni Beach Point",
            category="beach",
            description="The most vibrant and accessible beach area in Cox's Bazar, famous for beach horseback riding, shell markets, and breathtaking sunset views.",
            latitude=21.4320,
            longitude=91.9750,
            typical_duration_minutes=120,
            estimated_cost=200.0,
            image_url="https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
            tags=["sunset", "beach", "shopping"],
        ),
        Place(
            destination_id=cb.id,
            name="Inani Beach & Coral Reefs",
            category="beach",
            description="Quiet stretch of sea beach with unique sharp green and black coral boulders, calm azure water, and picturesque landscapes.",
            latitude=21.1865,
            longitude=92.0494,
            typical_duration_minutes=150,
            estimated_cost=500.0,
            image_url="https://images.unsplash.com/photo-1519046904884-53103b34b206",
            tags=["coral", "photography", "scenic"],
        ),
        Place(
            destination_id=cb.id,
            name="Himchari National Park & Waterfall",
            category="nature",
            description="Lush green hill forest offering panoramic clifftop views of the Bay of Bengal, serene hiking paths, and seasonal waterfalls.",
            latitude=21.3533,
            longitude=92.0289,
            typical_duration_minutes=90,
            estimated_cost=300.0,
            image_url="https://images.unsplash.com/photo-1448375240586-882707db888b",
            tags=["waterfall", "hiking", "viewpoint"],
        ),
        Place(
            destination_id=cb.id,
            name="Marine Drive Auto/Chander Gari Safari",
            category="scenic_drive",
            description="An 80-kilometer exhilarating scenic coastal drive between hills and the roaring sea.",
            latitude=21.3000,
            longitude=92.0300,
            typical_duration_minutes=180,
            estimated_cost=1500.0,
            image_url="https://images.unsplash.com/photo-1469854523086-cc02fe5d8800",
            tags=["drive", "adventure", "ocean view"],
        ),
    ]
    for p in cb_places:
        db.add(p)

    cb_hotels = [
        Hotel(
            destination_id=cb.id,
            name="Sayeman Beach Resort",
            category="resort",
            star_rating=5.0,
            price_per_night=8500.0,
            description="Iconic luxury beachfront resort featuring infinity pool overlooking the ocean, fine dining, and premier beachfront suites.",
            latitude=21.4180,
            longitude=91.9810,
            amenities=["pool", "wifi", "breakfast", "sea_view", "gym", "spa"],
            image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945",
        ),
        Hotel(
            destination_id=cb.id,
            name="Long Beach Hotel Cox's Bazar",
            category="hotel",
            star_rating=4.5,
            price_per_night=5500.0,
            description="Comfortable modern hotel in central hotel-motel zone with rooftop dining and spa amenities.",
            latitude=21.4290,
            longitude=91.9860,
            amenities=["wifi", "breakfast", "pool", "restaurant"],
            image_url="https://images.unsplash.com/photo-1582719478250-c89cae4dc85b",
        ),
        Hotel(
            destination_id=cb.id,
            name="Mermaid Beach Resort",
            category="boutique",
            star_rating=4.5,
            price_per_night=7200.0,
            description="Eco-friendly romantic cottages situated right beside Pechar Dwip with private beach access.",
            latitude=21.2800,
            longitude=92.0350,
            amenities=["beach_access", "wifi", "organic_food", "spa"],
            image_url="https://images.unsplash.com/photo-1520250497591-112f2f40a3f4",
        ),
    ]
    for h in cb_hotels:
        db.add(h)

    cb_restaurants = [
        Restaurant(
            destination_id=cb.id,
            name="Jhaubon Restaurant",
            cuisine_type=["Bangladeshi", "Seafood", "Fish Curry"],
            price_tier="$$",
            average_cost_per_person=650.0,
            description="Famous traditional restaurant renowned for fresh Rupchanda fish fry, Koral curry, and local vhorta platter.",
            latitude=21.4330,
            longitude=91.9780,
            image_url="https://images.unsplash.com/photo-1534422298391-e4f8c172dddb",
        ),
        Restaurant(
            destination_id=cb.id,
            name="Casablanca Beach Cafe",
            cuisine_type=["Continental", "Seafood", "Mocktails"],
            price_tier="$$$",
            average_cost_per_person=1200.0,
            description="Chic open-air beachfront lounge offering seafood platters, grilled lobster, and sunset mocktails.",
            latitude=21.4170,
            longitude=91.9820,
            image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
        ),
    ]
    for r in cb_restaurants:
        db.add(r)

    # 2. Sylhet
    sy = Destination(
        name="Sylhet",
        country="Bangladesh",
        region="Sylhet Division",
        description="The land of two leaves and a bud, featuring endless emerald tea gardens, crystal-clear rivers, swamps, and spiritual shrines.",
        latitude=24.8949,
        longitude=91.8687,
        best_time_to_visit="September to February",
        climate="Subtropical highland",
        currency="BDT",
        average_daily_cost=4500.0,
        image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb",
        tags=["tea garden", "waterfalls", "swamp forest", "nature"],
        safety_rating=4.8,
    )
    db.add(sy)
    await db.flush()

    sy_places = [
        Place(
            destination_id=sy.id,
            name="Ratargul Swamp Forest",
            category="nature",
            description="The only freshwater swamp forest in Bangladesh, exploring evergreen submerged trees via quiet wooden boats.",
            latitude=25.0033,
            longitude=91.9288,
            typical_duration_minutes=150,
            estimated_cost=800.0,
            image_url="https://images.unsplash.com/photo-1448375240586-882707db888b",
            tags=["boat ride", "forest", "photography"],
        ),
        Place(
            destination_id=sy.id,
            name="Bisnakandi Stone Quarry & River",
            category="nature",
            description="Stunning confluence where high Meghalaya mountain streams flow over millions of smooth river pebbles.",
            latitude=25.1764,
            longitude=91.8986,
            typical_duration_minutes=180,
            estimated_cost=1200.0,
            image_url="https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05",
            tags=["river", "mountains", "scenic"],
        ),
        Place(
            destination_id=sy.id,
            name="Lakkatura & Malnicherra Tea Estate",
            category="tea_garden",
            description="Historic lush tea estates with undulating green hills, walking trails, and fresh Ceylon tea tastings.",
            latitude=24.9312,
            longitude=91.8633,
            typical_duration_minutes=90,
            estimated_cost=200.0,
            image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb",
            tags=["tea", "nature", "walks"],
        ),
    ]
    for p in sy_places:
        db.add(p)

    sy_hotels = [
        Hotel(
            destination_id=sy.id,
            name="Grand Sultan Tea Resort & Golf",
            category="resort",
            star_rating=5.0,
            price_per_night=9500.0,
            description="Ultra-luxurious 5-star resort tucked inside tea hills with 3-tier temperature controlled swimming pools and golf course.",
            latitude=24.3160,
            longitude=91.7340,
            amenities=["golf", "pool", "spa", "wifi", "fine_dining"],
            image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945",
        ),
    ]
    for h in sy_hotels:
        db.add(h)

    sy_restaurants = [
        Restaurant(
            destination_id=sy.id,
            name="Panshi Restaurant",
            cuisine_type=["Bangladeshi", "Traditional", "Beef Shatkora"],
            price_tier="$$",
            average_cost_per_person=450.0,
            description="Legendary restaurant famous for authentic beef cooked with local citrus Shatkora, Akhni Biryani, and traditional sweets.",
            latitude=24.8910,
            longitude=91.8690,
            image_url="https://images.unsplash.com/photo-1555396273-367ea4eb4db5",
        )
    ]
    for r in sy_restaurants:
        db.add(r)

    await db.commit()
