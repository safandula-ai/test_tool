from __future__ import annotations

from utils.smoke_diagnostics import emit_smoke_diagnostics, sanitize_headers


def test_smoke_headers_are_sorted_and_sensitive_values_are_redacted():
    assert sanitize_headers(
        {
            "X-Request-Id": "request-123",
            "Set-Cookie": "session=secret",
            "Authorization": "Bearer secret",
        }
    ) == {
        "Authorization": "<redacted>",
        "Set-Cookie": "<redacted>",
        "X-Request-Id": "request-123",
    }


def test_smoke_diagnostics_write_visible_terminal_payload():
    lines = []

    class Terminal:
        def write_line(self, value):
            lines.append(value)

    class PluginManager:
        def get_plugin(self, name):
            return Terminal() if name == "terminalreporter" else None

    class Config:
        pluginmanager = PluginManager()

    payload = emit_smoke_diagnostics(
        Config(),
        check="backend-gateway-health",
        method="GET",
        url="https://example.test/health",
        status=200,
        elapsed_ms=12.345,
        headers={"server": "example", "set-cookie": "secret"},
    )

    assert payload["elapsed_ms"] == 12.3
    assert payload["response_headers"]["set-cookie"] == "<redacted>"
    assert "https://example.test/health" in lines[0]
    assert '"server": "example"' in lines[0]
