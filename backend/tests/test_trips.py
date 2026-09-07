import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_trip_crud_and_duplication(client: AsyncClient, auth_headers: dict):
    # 1. Create Trip
    trip_payload = {
        "title": "Cox's Bazar Weekend Tour",
        "destination": "Cox's Bazar",
        "start_date": "2026-10-01",
        "end_date": "2026-10-03",
        "travelers_count": 2,
        "total_budget": 20000.0,
        "currency": "BDT",
        "travel_style": "beach",
        "description": "Fun weekend on the world's longest beach.",
    }
    create_resp = await client.post("/api/v1/trips", json=trip_payload, headers=auth_headers)
    assert create_resp.status_code == 201
    trip = create_resp.json()
    assert trip["title"] == "Cox's Bazar Weekend Tour"
    assert trip["duration_days"] == 3
    assert len(trip["days"]) == 3
    trip_id = trip["id"]

    # 2. Get Trip by ID
    get_resp = await client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == trip_id

    # 3. Update Trip
    update_resp = await client.put(
        f"/api/v1/trips/{trip_id}",
        json={"is_favorite": True, "total_budget": 25000.0},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["is_favorite"] is True
    assert update_resp.json()["total_budget"] == 25000.0

    # 4. Duplicate Trip
    dup_resp = await client.post(f"/api/v1/trips/{trip_id}/duplicate", headers=auth_headers)
    assert dup_resp.status_code == 200
    dup_trip = dup_resp.json()
    assert "Copy of" in dup_trip["title"]
    assert dup_trip["id"] != trip_id
