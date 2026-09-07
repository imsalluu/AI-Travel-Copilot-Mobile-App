import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_registration_and_login(client: AsyncClient):
    # 1. Register
    reg_payload = {
        "email": "newuser@example.com",
        "password": "secretpassword123",
        "full_name": "Rahim Khan",
        "home_country": "Bangladesh",
        "home_currency": "BDT",
    }
    reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    data = reg_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["email"] == "newuser@example.com"

    # 2. Login
    login_payload = {
        "email": "newuser@example.com",
        "password": "secretpassword123",
    }
    login_resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data

    # 3. Get /me
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "newuser@example.com"
    assert me_data["full_name"] == "Rahim Khan"


@pytest.mark.asyncio
async def test_invalid_login(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={"email": "wrong@example.com", "password": "wrong"})
    assert resp.status_code == 401
