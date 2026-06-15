from __future__ import annotations

import httpx
import pytest

from utils.test_diagnostics import TestDiagnosticRecorder, httpx_event_hooks


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
