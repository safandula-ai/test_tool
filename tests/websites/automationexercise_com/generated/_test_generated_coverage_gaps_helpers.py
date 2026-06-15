"""Helper functions for generated coverage tests."""

from __future__ import annotations

import httpx
from uuid import uuid4

from api_clients.automation_exercise_client import build_account_payload


def default_request_payload(request_parameters: str | None) -> dict[str, str]:
    payload: dict[str, str] = {}
    if not request_parameters:
        return payload
    for raw_parameter in request_parameters.split(","):
        parameter = raw_parameter.strip()
        if not parameter:
            continue
        name = parameter.split("(", 1)[0].strip().replace(" ", "_")
        if not name:
            continue
        if name == "email":
            payload[name] = f"generated-{uuid4().hex[:10]}@example.com"
        elif name == "password":
            payload[name] = "secret-password"
        elif name == "search_product":
            payload[name] = "top"
        else:
            payload[name] = "test"
    return payload


def generated_account_payload(test_name: str, *, password: str = "secret-password") -> dict[str, str]:
    email = f"{test_name}-{uuid4().hex[:10]}@example.com"
    return build_account_payload("Generated User", email, password)


async def cleanup_generated_account(
    client: httpx.AsyncClient,
    base_url: str,
    payload: dict[str, str] | None,
) -> None:
    if not payload:
        return
    try:
        await client.request(
            "DELETE",
            f"{base_url}/api/deleteAccount",
            data={"email": payload["email"], "password": payload["password"]},
        )
    except Exception:
        return


async def automationexercise_request_kwargs(
    client: httpx.AsyncClient,
    *,
    base_url: str,
    test_name: str,
    path: str,
    method: str,
    scenario: str,
    request_parameters: str | None,
) -> tuple[dict[str, object], dict[str, str] | None]:
    scenario_lower = scenario.lower()
    request_kwargs: dict[str, object] = {}
    cleanup_payload: dict[str, str] | None = None

    if path == "/api/createAccount" and method == "POST":
        cleanup_payload = generated_account_payload(test_name)
        request_kwargs["data"] = cleanup_payload
        return request_kwargs, cleanup_payload

    if path == "/api/deleteAccount" and method == "DELETE":
        cleanup_payload = generated_account_payload(test_name)
        await client.request(
            "POST",
            f"{base_url}/api/createAccount",
            data=cleanup_payload,
        )
        request_kwargs["data"] = {
            "email": cleanup_payload["email"],
            "password": cleanup_payload["password"],
        }
        return request_kwargs, None

    if path == "/api/updateAccount" and method == "PUT":
        original_payload = generated_account_payload(test_name)
        await client.request(
            "POST",
            f"{base_url}/api/createAccount",
            data=original_payload,
        )
        cleanup_payload = dict(original_payload)
        cleanup_payload["password"] = "updated-secret-password"
        cleanup_payload["firstname"] = "Updated"
        request_kwargs["data"] = cleanup_payload
        return request_kwargs, cleanup_payload

    if path == "/api/getUserDetailByEmail" and method == "GET":
        cleanup_payload = generated_account_payload(test_name)
        await client.request(
            "POST",
            f"{base_url}/api/createAccount",
            data=cleanup_payload,
        )
        request_kwargs["params"] = {"email": cleanup_payload["email"]}
        return request_kwargs, cleanup_payload

    if path == "/api/verifyLogin" and method == "POST":
        if "valid details" in scenario_lower:
            cleanup_payload = generated_account_payload(test_name)
            await client.request(
                "POST",
                f"{base_url}/api/createAccount",
                data=cleanup_payload,
            )
            request_kwargs["data"] = {
                "email": cleanup_payload["email"],
                "password": cleanup_payload["password"],
            }
            return request_kwargs, cleanup_payload
        if "without email parameter" in scenario_lower:
            request_kwargs["data"] = {"password": "secret-password"}
            return request_kwargs, cleanup_payload
        if "without password parameter" in scenario_lower:
            request_kwargs["data"] = {"email": f"generated-{uuid4().hex[:10]}@example.com"}
            return request_kwargs, cleanup_payload
        if "invalid details" in scenario_lower:
            request_kwargs["data"] = {
                "email": f"missing-{uuid4().hex[:10]}@example.com",
                "password": "wrong-password",
            }
            return request_kwargs, cleanup_payload

    if path == "/api/searchProduct" and method == "POST":
        if "without search_product parameter" in scenario_lower:
            request_kwargs["data"] = {}
        else:
            request_kwargs["data"] = {"search_product": "top"}
        return request_kwargs, cleanup_payload

    payload = default_request_payload(request_parameters)
    if payload:
        if method == "GET":
            request_kwargs["params"] = payload
        else:
            request_kwargs["data"] = payload
    return request_kwargs, cleanup_payload
