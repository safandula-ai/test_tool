from __future__ import annotations

import json
from urllib.parse import parse_qs

import httpx


def build_transport() -> httpx.MockTransport:
    """Return a mock transport for offline API tests."""

    automation_accounts: set[str] = set()

    def handler(request: httpx.Request) -> httpx.Response:
        """Map simple API routes to deterministic responses."""
        if request.method == "GET" and request.url.path == "/api/users":
            page = int(request.url.params.get("page", "1"))
            users = {
                1: [
                    {
                        "id": 1,
                        "email": "george.bluth@reqres.in",
                        "first_name": "George",
                        "last_name": "Bluth",
                        "avatar": "https://reqres.in/img/faces/1-image.jpg",
                    }
                ],
                2: [
                    {
                        "id": 2,
                        "email": "janet.weaver@reqres.in",
                        "first_name": "Janet",
                        "last_name": "Weaver",
                        "avatar": "https://reqres.in/img/faces/2-image.jpg",
                    }
                ],
            }
            return httpx.Response(
                200,
                json={
                    "page": page,
                    "per_page": 1,
                    "total": 2,
                    "total_pages": 2,
                    "data": users.get(page, []),
                },
            )
        if request.method == "POST" and request.url.path == "/api/createAccount":
            payload = parse_qs(request.content.decode("utf-8"))
            email = payload.get("email", [""])[0]
            if email in automation_accounts:
                return httpx.Response(200, json={"responseCode": 400, "message": "Email already exists!"})
            automation_accounts.add(email)
            return httpx.Response(200, json={"responseCode": 201, "message": "User created!"})
        if request.method == "DELETE" and request.url.path == "/api/deleteAccount":
            payload = parse_qs(request.content.decode("utf-8"))
            automation_accounts.discard(payload.get("email", [""])[0])
            return httpx.Response(200, json={"responseCode": 200, "message": "Account deleted!"})
        if request.method == "GET" and request.url.path == "/api/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.method == "POST" and request.url.path == "/api/users":
            payload = json.loads(request.content.decode("utf-8") or "{}")
            return httpx.Response(201, json={"id": 1, **payload})
        if request.method == "GET" and request.url.path.startswith("/api/users/"):
            user_id = request.url.path.rsplit("/", 1)[-1]
            return httpx.Response(200, json={"id": int(user_id), "name": "Test User", "email": "user@example.com"})
        return httpx.Response(404, json={"detail": "Not found"})

    return httpx.MockTransport(handler)
