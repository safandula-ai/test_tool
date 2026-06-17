"""Automation Exercise account API client."""

from __future__ import annotations

from pathlib import Path

import httpx

from api_clients.base_client import BaseClient
from utils.schema_validator import load_schema, validate


RESPONSE_SCHEMA = load_schema(
    Path(__file__).resolve().parent.parent / "schemas" / "automation_response.schema.json"
)

CREATE_ACCOUNT_ENDPOINT = "POST /api/createAccount"
DELETE_ACCOUNT_ENDPOINT = "DELETE /api/deleteAccount"


def _validated_payload(response: httpx.Response) -> dict:
    """Parse and validate an Automation Exercise API response."""
    response.raise_for_status()
    payload = response.json()
    validate(payload, RESPONSE_SCHEMA)
    return payload


class AutomationExerciseClient(BaseClient):
    """Create and remove test accounts through the official practice API."""

    async def create_account(self, payload: dict[str, str]) -> dict:
        """Create an account and return the API's application-level response."""
        response = await self.client.post(CREATE_ACCOUNT_ENDPOINT.split(" ", 1)[1], data=payload)
        return _validated_payload(response)

    async def delete_account(self, email: str, password: str) -> dict:
        """Delete a test account by credentials."""
        response = await self.client.request(
            "DELETE",
            DELETE_ACCOUNT_ENDPOINT.split(" ", 1)[1],
            data={"email": email, "password": password},
        )
        return _validated_payload(response)


def build_account_payload(name: str, email: str, password: str) -> dict[str, str]:
    """Build the complete form payload required by the account API."""
    return {
        "name": name,
        "email": email,
        "password": password,
        "title": "Mr",
        "birth_date": "1",
        "birth_month": "1",
        "birth_year": "1990",
        "firstname": "Test",
        "lastname": "User",
        "company": "Test Company",
        "address1": "Test Street 1",
        "address2": "Suite 1",
        "country": "Canada",
        "zipcode": "00-001",
        "state": "Test State",
        "city": "Test City",
        "mobile_number": "123456789",
    }
