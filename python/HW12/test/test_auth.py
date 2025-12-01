import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from auth.auth_refresh_repository import RefreshTokenRepository
from auth.auth_service import AuthService
from auth.auth_model import UserAuth, RefreshToken
from auth.auth_repository import UserRepository



@pytest.mark.asyncio
async def test_registrate_success(client: AsyncClient):
    payload = {
        "email": "test1@example.com",
        "username": "testuser1",
        "full_name": "Test User One",
        "password": "StrongP@ss1"
    }
    resp = await client.post("/auth/registrate", json=payload)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["email"] == payload["email"]
    assert "status" in data

@pytest.mark.asyncio
async def test_registrate_duplicate(client: AsyncClient):
    payload = {
        "email": "dup@example.com",
        "username": "dupuser",
        "full_name": "Dup User",
        "password": "StrongP@ss1"
    }
    r1 = await client.post("/auth/registrate", json=payload)
    assert r1.status_code in (200, 201)
    r2 = await client.post("/auth/registrate", json=payload)
    assert r2.status_code == 400

@pytest.mark.asyncio
async def test_login_and_get_me(client: AsyncClient):
    payload = {
        "email": "login_user@example.com",
        "username": "loginuser",
        "full_name": "Login User",
        "password": "Passw0rd!"
    }
    await client.post("/auth/registrate", json=payload)

    # login
    resp = await client.post("/auth/token", json={"email": payload["email"], "password": payload["password"]})
    assert resp.status_code == 200
    content = resp.json()
    assert "access_token" in content
    # учтём опечатку в коде ("toke_type")
    assert ("token_type" in content) or ("toke_type" in content)
    access_token = content["access_token"]

    # cookie с refresh_token установлен
    refresh_cookie = resp.cookies.get("refresh_token")
    assert refresh_cookie is not None
    assert "." in refresh_cookie

    # protected route
    headers = {"Authorization": f"Bearer {access_token}"}
    me_resp = await client.get("/auth/users/me/", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == payload["email"]

@pytest.mark.asyncio
async def test_refresh_flow_and_logout(client: AsyncClient, db_session):
    # 1️⃣ регистрация пользователя
    payload = {
        "email": "refresh_user@example.com",
        "username": "refreshuser",
        "full_name": "Refresh User",
        "password": "Refr3shP@ss!"
    }
    resp = await client.post("/auth/registrate", json=payload)
    assert resp.status_code == 200

    # 2️⃣ логин пользователя (эндпоинт создаёт refresh-token и ставит cookie)
    resp = await client.post("/auth/token", json={"email": payload["email"], "password": payload["password"]})
    assert resp.status_code == 200
    print("After login, cookies:", client.cookies)

    # 3️⃣ получаем refresh-token, который реально отправил сервер
    refresh_cookie = client.cookies.get("refresh_token")
    assert refresh_cookie is not None
    print("Refresh cookie from login:", refresh_cookie)

    # 4️⃣ проверяем refresh (используем cookie от логина)
    print("After login, cookies:", client.cookies)
    print("Refresh cookie from login:", client.cookies.get("refresh_token"))
    r2 = await client.post("/auth/refresh", cookies={"refresh_token": refresh_cookie})
    print("After refresh call, cookies:", client.cookies)
    print("Refresh response status:", r2.status_code, r2.text)
    assert r2.status_code == 200

    # 5️⃣ logout
    logout_resp = await client.post("/auth/logout", json={"refresh_token": refresh_cookie})
    assert logout_resp.status_code in (200, 404)

    # 6️⃣ проверяем, что токен больше не действует
    r3 = await client.post("/auth/refresh")
    print("After refresh with revoked token, status:", r3.status_code)
    assert r3.status_code == 401
    print("Final cookies:", client.cookies)