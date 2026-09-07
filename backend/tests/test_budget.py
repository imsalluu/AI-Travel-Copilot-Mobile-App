import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_budget_and_expenses_lifecycle(client: AsyncClient, auth_headers: dict):
    # 1. Create a trip
    trip_payload = {
        "title": "Sylhet Nature Retreat",
        "destination": "Sylhet",
        "start_date": "2026-11-10",
        "end_date": "2026-11-12",
        "total_budget": 15000.0,
        "currency": "BDT",
    }
    trip_resp = await client.post("/api/v1/trips", json=trip_payload, headers=auth_headers)
    trip_id = trip_resp.json()["id"]

    # 2. Fetch budget summary
    b_resp = await client.get(f"/api/v1/budget/trips/{trip_id}", headers=auth_headers)
    assert b_resp.status_code == 200
    b_data = b_resp.json()
    assert b_data["total_budget"] == 15000.0
    assert len(b_data["category_breakdowns"]) >= 6

    # 3. Add expense
    exp_payload = {
        "category": "food",
        "title": "Dinner at Panshi Restaurant",
        "amount": 850.0,
        "payment_method": "cash",
    }
    exp_resp = await client.post(f"/api/v1/budget/trips/{trip_id}/expenses", json=exp_payload, headers=auth_headers)
    assert exp_resp.status_code == 201
    assert exp_resp.json()["amount"] == 850.0

    # 4. Check updated summary
    b_resp2 = await client.get(f"/api/v1/budget/trips/{trip_id}", headers=auth_headers)
    b_data2 = b_resp2.json()
    assert b_data2["total_spent"] == 850.0
    assert b_data2["remaining_budget"] == 14150.0
