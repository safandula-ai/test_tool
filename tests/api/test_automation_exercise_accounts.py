"""Automation Exercise account API tests."""

from __future__ import annotations

import pytest

from api_clients.automation_exercise_client import AutomationExerciseClient, build_account_payload
from coverage_agent.decorators import covers


@pytest.mark.api
@pytest.mark.asyncio
@covers(type="api", target="POST /api/createAccount", priority="critical", template="APIContractTemplate")
@covers(type="api", target="DELETE /api/deleteAccount", priority="high", template="APIContractTemplate")
async def test_duplicate_account_is_rejected_and_account_can_be_cleaned_up(api_client):
    """Verify account creation, duplicate rejection, and cleanup."""
    client = AutomationExerciseClient(api_client)
    payload = build_account_payload("Test User", "existing@example.com", "secret-password")

    created = await client.create_account(payload)
    duplicate = await client.create_account(payload)
    deleted = await client.delete_account(payload["email"], payload["password"])

    assert created == {"responseCode": 201, "message": "User created!"}
    assert duplicate["responseCode"] == 400
    assert "exists" in duplicate["message"].lower()
    assert deleted == {"responseCode": 200, "message": "Account deleted!"}
