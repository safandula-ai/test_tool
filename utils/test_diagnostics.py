"""Per-test diagnostics for HTTP, browser, and framework execution."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, ClassVar
from urllib.parse import parse_qsl

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
    log_lines: list[str] = field(default_factory=list)

    def record(self, category: str, **values: Any) -> None:
        """Append one structured diagnostic event to the current test payload."""
        self.events.append({"category": category, **values})

    def payload(self, item: pytest.Item) -> dict[str, Any]:
        """Build the final JSON-serializable diagnostics payload for a pytest item."""
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


def render_test_diagnostics(
    item: pytest.Item,
    recorder: TestDiagnosticRecorder,
) -> str:
    """Return the rendered per-test diagnostics payload."""
    return json.dumps(recorder.payload(item), indent=2, sort_keys=True)


def append_report_diagnostics(
    report: pytest.TestReport,
    rendered: str,
    log_lines: list[str] | None = None,
) -> None:
    """Publish diagnostics into native pytest captured-output sections."""
    when = report.when
    report.sections.append((f"Captured stdout {when}", f"TEST DIAGNOSTICS\n{rendered}"))
    if log_lines:
        report.sections.append((f"Captured log {when}", "\n".join(log_lines)))


def httpx_event_hooks(recorder: TestDiagnosticRecorder) -> dict[str, list[Any]]:
    """Build async HTTPX hooks that record requests and sanitized responses."""

    def decode_payload(content: bytes, content_type: str | None) -> Any:
        if not content:
            return None
        normalized_type = (content_type or "").split(";", 1)[0].strip().lower()
        if normalized_type == "application/x-www-form-urlencoded":
            return dict(parse_qsl(content.decode("utf-8", errors="replace")))
        try:
            return json.loads(content.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            text_content = content.decode("utf-8", errors="replace")
            return text_content if len(text_content) < 1000 else text_content[:1000] + "... [truncated]"

    async def on_request(request: httpx.Request) -> None:
        request.extensions["diagnostic_started"] = time.perf_counter()

        payload = None
        try:
            content = request.content
        except Exception:
            content = b""
        if not content:
            try:
                await request.aread()
                content = request.content
            except Exception:
                content = b""
        if content:
            try:
                payload = decode_payload(content, request.headers.get("content-type"))
            except Exception:
                payload = "<unreadable content>"

        recorder.record(
            "http_request",
            method=request.method,
            url=str(request.url),
            request_headers=sanitize_headers(dict(request.headers)),
            payload=payload,
        )

    async def on_response(response: httpx.Response) -> None:
        started = response.request.extensions.get("diagnostic_started")
        elapsed_ms = (
            (time.perf_counter() - started) * 1000 if isinstance(started, float) else None
        )
        payload = None
        try:
            await response.aread()
            content = response.content
            if content:
                try:
                    payload = response.json()
                except json.JSONDecodeError:
                    payload = decode_payload(content, response.headers.get("content-type"))
        except Exception:
            payload = "<unreadable content>"

        recorder.record(
            "http_response",
            method=response.request.method,
            url=str(response.url),
            status=response.status_code,
            elapsed_ms=round(elapsed_ms, 1) if elapsed_ms is not None else None,
            response_headers=sanitize_headers(dict(response.headers)),
            payload=payload,
        )

    return {"request": [on_request], "response": [on_response]}


def emit_test_diagnostics(
    pytestconfig: pytest.Config,
    item: pytest.Item,
    recorder: TestDiagnosticRecorder,
) -> dict[str, Any]:
    """Write diagnostics to terminal and per-test capture."""
    payload = recorder.payload(item)
    rendered = render_test_diagnostics(item, recorder)
    print(f"TEST DIAGNOSTICS\n{rendered}", flush=True)
    terminal = pytestconfig.pluginmanager.get_plugin("terminalreporter")
    if terminal is not None:
        terminal.write_line(f"TEST DIAGNOSTICS\n{rendered}")
    return payload
