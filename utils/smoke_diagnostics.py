"""Visible terminal diagnostics for website smoke checks."""

from __future__ import annotations

import json
import os
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


def _terminal_diagnostics_enabled(pytestconfig: pytest.Config) -> bool:
    """Return whether smoke diagnostics should be written to the terminal."""
    try:
        if pytestconfig.getoption("--quiet-diagnostics"):
            return False
    except Exception:
        pass
    return os.getenv("TERMINAL_DIAGNOSTICS", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


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
    """Return smoke diagnostics and optionally publish them to the terminal."""
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
    if terminal is not None and _terminal_diagnostics_enabled(pytestconfig):
        terminal.write_line(f"SMOKE DIAGNOSTICS\n{rendered}")

    return payload
