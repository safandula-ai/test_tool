"""Live Automation Exercise account API tests."""

from __future__ import annotations

import uuid

import httpx
import pytest

from api_clients.automation_exercise_client import (
    AutomationExerciseClient,
    build_account_payload,
)
from coverage_agent.decorators import covers
from tests.websites.automationexercise_com.suite_config import BASE_URL
from utils.test_diagnostics import httpx_event_hooks


@pytest.mark.api
@pytest.mark.asyncio
@pytest.mark.integration
@covers(
    type="api",
    target="POST /api/createAccount",
    priority="critical",
    template="APIContractTemplate",
)
@covers(
    type="api",
    target="DELETE /api/deleteAccount",
    priority="high",
    template="APIContractTemplate",
)
async def test_duplicate_account_is_rejected_and_live_account_can_be_cleaned_up(
    settings,
    test_diagnostics,
):
    """Verify the live account API can create, reject duplicates, and delete."""
    email = f"test_{uuid.uuid4().hex[:12]}@example.com"
    payload = build_account_payload("Test User", email, "secret-password")
    test_diagnostics.record(
        "test_surface",
        mode="live_api",
        url=f"{BASE_URL}/api/createAccount",
        payload={
            "base_url": BASE_URL,
            "email": email,
            "create_endpoint": "/api/createAccount",
            "delete_endpoint": "/api/deleteAccount",
        },
    )

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=settings.http_timeout,
        follow_redirects=True,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        client = AutomationExerciseClient(live_client)
        created = await client.create_account(payload)
        duplicate = await client.create_account(payload)
        deleted = await client.delete_account(payload["email"], payload["password"])

    test_diagnostics.record(
        "api_account_flow",
        payload={
            "created": created,
            "duplicate": duplicate,
            "deleted": deleted,
        },
    )
    assert created == {"responseCode": 201, "message": "User created!"}
    assert duplicate["responseCode"] == 400
    assert "exists" in duplicate["message"].lower()
    assert deleted == {"responseCode": 200, "message": "Account deleted!"}
