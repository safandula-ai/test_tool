"""Visible terminal and Allure diagnostics for website smoke checks."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import pytest


SENSITIVE_HEADER_TOKENS = (
    "authorization",
    "cookie",
    "api-key",
    "apikey",
    "token",
)


def sanitize_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """Return sorted response headers with credential-bearing values removed."""
    sanitized: dict[str, str] = {}
    for name, value in sorted(headers.items(), key=lambda item: item[0].lower()):
        normalized = name.lower()
        sanitized[name] = (
            "<redacted>"
            if any(token in normalized for token in SENSITIVE_HEADER_TOKENS)
            else value
        )
    return sanitized


def emit_smoke_diagnostics(
    pytestconfig: pytest.Config,
    *,
    check: str,
    method: str,
    url: str,
    status: int,
    elapsed_ms: float,
    headers: Mapping[str, str],
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Print a smoke result despite capture and attach the same JSON to Allure."""
    payload: dict[str, Any] = {
        "check": check,
        "method": method,
        "url": url,
        "status": status,
        "elapsed_ms": round(elapsed_ms, 1),
        "response_headers": sanitize_headers(headers),
    }
    if details:
        payload["details"] = dict(details)

    rendered = json.dumps(payload, indent=2, sort_keys=True)
    terminal = pytestconfig.pluginmanager.get_plugin("terminalreporter")
    if terminal is not None:
        terminal.write_line(f"SMOKE DIAGNOSTICS\n{rendered}")

    try:
        import allure

        allure.attach(
            rendered,
            name=f"smoke-{check}",
            attachment_type=allure.attachment_type.JSON,
        )
    except (ImportError, RuntimeError):
        pass
    return payload
