import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ai_agent_trip_generation_and_conversational_editing(client: AsyncClient, auth_headers: dict):
    # 1. Send AI travel planning prompt
    prompt_payload = {
        "message": "I want to visit Cox's Bazar for 3 days with a budget of 20,000 BDT.",
    }
    chat_resp = await client.post("/api/v1/chat/message", json=prompt_payload, headers=auth_headers)
    assert chat_resp.status_code == 200
    msg = chat_resp.json()
    assert msg["role"] == "assistant"
    assert msg["message_type"] == "itinerary_card"
    assert msg["structured_data"] is not None

    card = msg["structured_data"]
    assert card["destination"] == "Cox's Bazar"
    assert card["duration_days"] == 3
    assert len(card["days"]) == 3
    assert "trip_id" in card
    trip_id = card["trip_id"]

    # 2. Conversational modification: "Make day 2 less busy"
    modify_payload = {
        "message": "Make day 2 less busy",
        "trip_id": trip_id,
        "conversation_id": msg["conversation_id"],
    }
    mod_resp = await client.post("/api/v1/chat/message", json=modify_payload, headers=auth_headers)
    assert mod_resp.status_code == 200
    mod_msg = mod_resp.json()
    assert mod_msg["message_type"] == "itinerary_card"
    assert "relaxed pace" in mod_msg["content"].lower() or "adjusted" in mod_msg["content"].lower()
