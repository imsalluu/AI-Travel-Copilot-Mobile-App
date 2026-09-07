import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_weather_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/weather?destination=Cox's Bazar&duration_days=3")
    assert resp.status_code == 200
    data = resp.json()
    assert data["destination"] == "Cox's Bazar"
    assert "current_temperature" in data
    assert "condition" in data
    assert len(data["daily_forecasts"]) >= 3
    assert len(data["travel_advisories"]) > 0
