from __future__ import annotations

from pathlib import Path

import pytest

from api_clients.user_client import UserClient
from coverage_agent.decorators import covers
from utils.schema_validator import load_schema, validate


@pytest.mark.api
@pytest.mark.asyncio
@covers(type="api", target="GET /health", priority="critical", template="APIContractTemplate")
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
@covers(type="api", target="POST /users", priority="high", template="APIContractTemplate")
async def test_create_user_contract(api_client):
    """Verify user creation returns a payload matching the schema."""
    client = UserClient(api_client)
    payload = {"name": "Test User", "email": "user@example.com"}
    response = await client.create_user(payload)
    assert response.status_code == 201

    schema = load_schema(Path("schemas/user.schema.json"))
    validate(response.json(), schema)
