"""Per-test diagnostics for HTTP, browser, and framework execution."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, ClassVar

import httpx
import pytest

from utils.smoke_diagnostics import sanitize_headers


@dataclass
class TestDiagnosticRecorder:
    """Collect sanitized diagnostic events for one pytest item."""

    __test__: ClassVar[bool] = False

    nodeid: str
    started: float = field(default_factory=time.perf_counter)
    events: list[dict[str, Any]] = field(default_factory=list)

    def record(self, category: str, **values: Any) -> None:
        self.events.append({"category": category, **values})

    def payload(self, item: pytest.Item) -> dict[str, Any]:
        call = getattr(item, "rep_call", None)
        setup = getattr(item, "rep_setup", None)
        outcome = "unknown"
        if call is not None:
            outcome = call.outcome
        elif setup is not None:
            outcome = setup.outcome
        return {
            "test": self.nodeid,
            "outcome": outcome,
            "duration_ms": round((time.perf_counter() - self.started) * 1000, 1),
            "markers": sorted(marker.name for marker in item.iter_markers()),
            "events": self.events,
        }


def httpx_event_hooks(recorder: TestDiagnosticRecorder) -> dict[str, list[Any]]:
    """Build async HTTPX hooks that record requests and sanitized responses."""

    async def on_request(request: httpx.Request) -> None:
        request.extensions["diagnostic_started"] = time.perf_counter()
        recorder.record(
            "http_request",
            method=request.method,
            url=str(request.url),
            request_headers=sanitize_headers(dict(request.headers)),
        )

    async def on_response(response: httpx.Response) -> None:
        started = response.request.extensions.get("diagnostic_started")
        elapsed_ms = (
            (time.perf_counter() - started) * 1000 if isinstance(started, float) else None
        )
        recorder.record(
            "http_response",
            method=response.request.method,
            url=str(response.url),
            status=response.status_code,
            elapsed_ms=round(elapsed_ms, 1) if elapsed_ms is not None else None,
            response_headers=sanitize_headers(dict(response.headers)),
        )

    return {"request": [on_request], "response": [on_response]}


def emit_test_diagnostics(
    pytestconfig: pytest.Config,
    item: pytest.Item,
    recorder: TestDiagnosticRecorder,
) -> dict[str, Any]:
    """Write diagnostics to terminal, per-test capture, and Allure."""
    payload = recorder.payload(item)
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    print(f"TEST DIAGNOSTICS\n{rendered}", flush=True)
    terminal = pytestconfig.pluginmanager.get_plugin("terminalreporter")
    if terminal is not None:
        terminal.write_line(f"TEST DIAGNOSTICS\n{rendered}")
    try:
        import allure

        allure.attach(
            rendered,
            name="test-diagnostics",
            attachment_type=allure.attachment_type.JSON,
        )
    except (ImportError, RuntimeError):
        pass
    return payload
