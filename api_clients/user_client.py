from __future__ import annotations

import httpx

from api_clients.base_client import BaseClient


class UserClient(BaseClient):
    """API client for user-related endpoints."""

    async def get_user(self, user_id: int) -> httpx.Response:
        """Fetch a single user by identifier."""
        return await self.get(f"/api/users/{user_id}")

    async def create_user(self, payload: dict) -> httpx.Response:
        """Create a user record from the provided payload."""
        return await self.post("/api/users", json=payload)

    async def health(self) -> httpx.Response:
        """Check whether the API health endpoint is reachable."""
        return await self.get("/api/health")
