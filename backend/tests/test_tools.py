import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.tools.travel_tools import TravelToolSuite, get_all_tool_definitions
from app.api.v1.endpoints.destinations import _seed_default_destinations


@pytest.mark.asyncio
async def test_travel_tools_suite(db_session: AsyncSession):
    # Seed destinations
    await _seed_default_destinations(db_session)
    tools = TravelToolSuite(db_session)

    # 1. Search places
    places = await tools.search_places("Cox's Bazar")
    assert len(places) > 0
    assert any("Beach" in p["name"] for p in places)

    # 2. Get place details
    details = await tools.get_place_details("Laboni Beach Point")
    assert details["name"] == "Laboni Beach Point"
    assert "estimated_cost" in details

    # 3. Search hotels
    hotels = await tools.search_hotels("Cox's Bazar")
    assert len(hotels) > 0

    # 4. Search restaurants
    rests = await tools.search_restaurants("Cox's Bazar")
    assert len(rests) > 0

    # 5. Distance and Travel Time
    dist = await tools.get_distance(21.4272, 92.0058, 21.1865, 92.0494)
    assert dist["distance_km"] > 0
    dur = await tools.get_travel_time(21.4272, 92.0058, 21.1865, 92.0494, mode="drive")
    assert dur["travel_time_minutes"] > 0

    # 6. Budget calculations
    budget = await tools.calculate_trip_budget(total_budget=20000.0, duration_days=3)
    assert budget["total_budget"] == 20000.0
    assert budget["allocations"]["hotel_budget"] > 0

    # 7. Currency rate
    rate = await tools.get_currency_rate("USD", "BDT")
    assert rate["exchange_rate"] > 100.0

    # Verify tool definitions schema list
    defs = get_all_tool_definitions()
    assert len(defs) >= 8
