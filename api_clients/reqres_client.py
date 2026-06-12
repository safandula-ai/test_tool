"""ReqRes API client with pagination and contract validation."""

from __future__ import annotations

from pathlib import Path

import httpx

from api_clients.base_client import BaseClient
from utils.schema_validator import load_schema, validate


SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


class ReqResClient(BaseClient):
    """Retrieve and validate users from the ReqRes API."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize the client and load reusable response contracts."""
        super().__init__(client)
        self.page_schema = load_schema(SCHEMA_DIR / "reqres_users_page.schema.json")
        self.user_schema = load_schema(SCHEMA_DIR / "reqres_user.schema.json")

    async def list_users(self, page: int = 1) -> dict:
        """Fetch and validate one page of users."""
        response = await self.get("/api/users", params={"page": page})
        response.raise_for_status()
        payload = response.json()
        validate(payload, self.page_schema)
        for user in payload["data"]:
            validate(user, self.user_schema)
        return payload

    async def get_all_users(self) -> list[dict]:
        """Follow pagination metadata and return every validated user."""
        first_page = await self.list_users(page=1)
        users = list(first_page["data"])
        for page_number in range(2, first_page["total_pages"] + 1):
            users.extend((await self.list_users(page=page_number))["data"])
        return users
