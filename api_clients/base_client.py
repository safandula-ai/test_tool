from __future__ import annotations

import httpx


class BaseClient:
    """Shared async HTTP client wrapper for API resource classes."""

    def __init__(self, client: httpx.AsyncClient):
        """Store the underlying `httpx.AsyncClient` instance."""
        self.client = client

    async def get(self, path: str, **kwargs) -> httpx.Response:
        """Send a GET request to the configured API base URL."""
        return await self.client.get(path, **kwargs)

    async def post(self, path: str, **kwargs) -> httpx.Response:
        """Send a POST request to the configured API base URL."""
        return await self.client.post(path, **kwargs)
