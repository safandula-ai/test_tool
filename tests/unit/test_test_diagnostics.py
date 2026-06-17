from __future__ import annotations

import httpx
import pytest

from utils.test_diagnostics import (
    TestDiagnosticRecorder,
    append_report_diagnostics,
    emit_test_diagnostics,
    httpx_event_hooks,
)


@pytest.mark.asyncio
async def test_httpx_diagnostics_capture_url_status_timing_and_headers():
    recorder = TestDiagnosticRecorder("test_httpx_diagnostics")

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"x-request-id": "abc", "set-cookie": "secret=value"},
            json={"status": "ok"},
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        event_hooks=httpx_event_hooks(recorder),
    ) as client:
        response = await client.get(
            "https://example.test/health",
            headers={"authorization": "Bearer secret"},
        )

    assert response.status_code == 200
    request_event, response_event = recorder.events
    assert request_event["url"] == "https://example.test/health"
    assert request_event["request_headers"]["authorization"] == "<redacted>"
    assert response_event["status"] == 200
    assert response_event["response_headers"]["set-cookie"] == "<redacted>"
    assert response_event["elapsed_ms"] is not None


@pytest.mark.asyncio
async def test_httpx_diagnostics_capture_form_request_payload():
    recorder = TestDiagnosticRecorder("test_httpx_form_payload")

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"responseCode": 200, "message": "ok"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        event_hooks=httpx_event_hooks(recorder),
    ) as client:
        await client.post(
            "https://example.test/login",
            data={"email": "user@example.com", "password": "secret-password"},
        )

    request_event, response_event = recorder.events
    assert request_event["payload"] == {
        "email": "user@example.com",
        "password": "secret-password",
    }
    assert response_event["payload"] == {"responseCode": 200, "message": "ok"}


def test_emit_test_diagnostics_returns_payload_without_side_effects():
    recorder = TestDiagnosticRecorder("tests/unit/test_example.py::test_case")
    recorder.log_lines.extend(
        [
            "2026-06-15 15:00:00 | INFO | first message",
            "2026-06-15 15:00:01 | ERROR | second message",
        ]
    )

    terminal_lines: list[str] = []

    class FakeMarker:
        name = "unit"

    class FakeReport:
        outcome = "passed"

    class FakeItem:
        nodeid = "tests/unit/test_example.py::test_case"
        rep_call = FakeReport()

        def iter_markers(self):
            return [FakeMarker()]

    class Terminal:
        def write_line(self, value):
            terminal_lines.append(value)

    class PluginManager:
        def get_plugin(self, name):
            return Terminal() if name == "terminalreporter" else None

    class Config:
        pluginmanager = PluginManager()

    payload = emit_test_diagnostics(Config(), FakeItem(), recorder)

    assert payload["outcome"] == "passed"
    assert terminal_lines == []
    assert payload["test"] == "tests/unit/test_example.py::test_case"


def test_append_report_diagnostics_uses_native_pytest_capture_sections():
    class FakeReport:
        when = "call"
        sections: list[tuple[str, str]] = []

    report = FakeReport()
    append_report_diagnostics(
        report,
        "{\n  \"test\": \"tests/unit/test_example.py::test_case\"\n}",
        [
            "2026-06-15 15:00:00 | INFO | first message",
            "2026-06-15 15:00:01 | ERROR | second message",
        ],
    )

    assert report.sections == [
        (
            "Captured stdout call",
            "TEST DIAGNOSTICS\n{\n  \"test\": \"tests/unit/test_example.py::test_case\"\n}",
        ),
        (
            "Captured log call",
            "2026-06-15 15:00:00 | INFO | first message\n"
            "2026-06-15 15:00:01 | ERROR | second message",
        ),
    ]
