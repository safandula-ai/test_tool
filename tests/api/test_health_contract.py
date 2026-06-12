from __future__ import annotations

from pathlib import Path

import pytest

from api_clients.user_client import UserClient
from api_clients.reqres_client import ReqResClient
from config.settings import get_settings
from utils.schema_validator import load_schema, validate


@pytest.mark.api
@pytest.mark.asyncio
async def test_health_contract(api_client):
    """Verify the health endpoint responds with a valid contract."""
    client = UserClient(api_client)
    response = await client.health()
    assert response.status_code == 200

    payload = response.json()
    schema = {"type": "object", "required": ["status"], "properties": {"status": {"const": "ok"}}}
    validate(payload, schema)


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_user_contract(api_client):
    """Verify user creation returns a payload matching the schema."""
    client = UserClient(api_client)
    payload = {"name": "Test User", "email": "user@example.com"}
    response = await client.create_user(payload)
    assert response.status_code == 201

    schema = load_schema(Path("schemas/user.schema.json"))
    validate(response.json(), schema)


@pytest.mark.api
@pytest.mark.asyncio
async def test_reqres_client_collects_and_validates_all_user_pages(api_client):
    """Collect every mocked ReqRes page and validate each user contract."""
    users = await ReqResClient(api_client).get_all_users()
    assert [user["id"] for user in users] == [1, 2]


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(
    not (get_settings().run_live_tests and get_settings().reqres_api_key),
    reason="Set RUN_LIVE_TESTS=true and REQRES_API_KEY to call ReqRes",
)
async def test_live_reqres_users_follow_pagination(reqres_http_client):
    """Verify pagination and contracts against the live ReqRes service."""
    users = await ReqResClient(reqres_http_client).get_all_users()
    assert users
    assert len({user["id"] for user in users}) == len(users)
