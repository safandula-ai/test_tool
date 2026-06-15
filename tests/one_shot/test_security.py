"""Reusable one-shot security tests for a live website target.

Copy this file into a dedicated website suite and replace the route/selector constants below.
By default the target comes from `BASE_URL`; pass `--target-url` to override it.
"""

from __future__ import annotations

import os

import pytest

from coverage_agent.decorators import covers


DEFAULT_BASE_URL = os.getenv("BASE_URL", "https://example.test")
SECURITY_SEARCH_PATH = os.getenv("ONE_SHOT_SECURITY_SEARCH_PATH", "/")
SECURITY_SEARCH_INPUT_SELECTOR = os.getenv(
    "ONE_SHOT_SECURITY_SEARCH_INPUT_SELECTOR",
    "input[type='search'], input[name='search'], input[type='text']",
)
SECURITY_SEARCH_SUBMIT_SELECTOR = os.getenv(
    "ONE_SHOT_SECURITY_SEARCH_SUBMIT_SELECTOR",
    "button[type='submit'], input[type='submit']",
)
SECURITY_CONSENT_ROOT_SELECTOR = os.getenv("ONE_SHOT_SECURITY_CONSENT_ROOT_SELECTOR", ".fc-consent-root")
SECURITY_CONSENT_ACCEPT_SELECTOR = os.getenv(
    "ONE_SHOT_SECURITY_CONSENT_ACCEPT_SELECTOR",
    ".fc-cta-consent, button:has-text('Consent'), button:has-text('Accept')",
)


def _target_url(pytestconfig):
    return (pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL).rstrip("/")


def _require_live_target(pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")


async def _dismiss_consent_if_present(page) -> None:
    root = page.locator(SECURITY_CONSENT_ROOT_SELECTOR).first
    if await root.count() == 0:
        return
    accept_button = page.locator(SECURITY_CONSENT_ACCEPT_SELECTOR).first
    if await accept_button.is_visible():
        await accept_button.click(force=True)
    if await root.is_visible():
        await page.evaluate(
            """(rootSelector) => {
                const root = document.querySelector(rootSelector);
                if (root) {
                    root.remove();
                }
                const overlay = document.querySelector('.fc-dialog-overlay');
                if (overlay) {
                    overlay.remove();
                }
                document.body.style.overflow = 'auto';
            }""",
            SECURITY_CONSENT_ROOT_SELECTOR,
        )


@pytest.mark.security
@pytest.mark.ui
@pytest.mark.asyncio
@covers(
    type="ui",
    target="search-field-injection",
    priority="high",
    template="SecuritySanitizerTemplate",
    page="/",
    feature="feature:security",
)
async def test_search_rejects_reflected_xss_payload(
    page_factory,
    pytestconfig,
    settings,
    test_diagnostics,
):
    _require_live_target(pytestconfig, settings)
    base_url = _target_url(pytestconfig)
    xss_payload = '<script id="malicious-xss">window.__xss_executed = true;</script>'

    async with page_factory(base_url) as page:
        await page.goto(SECURITY_SEARCH_PATH, wait_until="domcontentloaded")
        await _dismiss_consent_if_present(page)
        await page.wait_for_load_state("networkidle")
        search_input = page.locator(SECURITY_SEARCH_INPUT_SELECTOR).first
        search_submit = page.locator(SECURITY_SEARCH_SUBMIT_SELECTOR).first
        if await search_input.count() == 0 or await search_submit.count() == 0:
            pytest.skip("Search controls are not available on the target page")
        await search_input.fill(xss_payload)
        await search_submit.click(force=True)
        await page.wait_for_load_state("networkidle")
        script_node = page.locator("script#malicious-xss")
        script_executed = await page.evaluate("() => Boolean(window.__xss_executed)")
        script_node_count = await script_node.count()
        rendered_markup = await page.locator("body").inner_html()
        reflected_input_value = await search_input.input_value()

    test_diagnostics.record(
        "security_xss_probe",
        route=SECURITY_SEARCH_PATH,
        payload=xss_payload,
        script_executed=script_executed,
        script_node_count=script_node_count,
        reflected_input_value=reflected_input_value,
    )
    assert not script_executed, "Executable script injection reached the browser context"
    assert script_node_count == 0, "Injected script tag was inserted into the DOM"
    assert '<script id="malicious-xss">' not in rendered_markup, (
        "Injected script tag was inserted into rendered markup"
    )
    assert reflected_input_value == xss_payload, (
        "Input value was unexpectedly transformed; review whether the target sanitizes or mutates input"
    )


@pytest.mark.security
@pytest.mark.api
@pytest.mark.asyncio
@covers(
    type="api",
    target="security-response-headers",
    priority="medium",
    template="APIContractTemplate",
    page="/",
    feature="feature:security",
)
async def test_http_security_defense_headers(
    page_factory,
    pytestconfig,
    settings,
    test_diagnostics,
):
    _require_live_target(pytestconfig, settings)
    base_url = _target_url(pytestconfig)
    required_headers = {
        "strict-transport-security": "HSTS protocol enforcement",
        "x-frame-options": "clickjacking mitigation",
        "content-security-policy": "content security policy",
    }

    async with page_factory(base_url) as page:
        response = await page.goto("/", wait_until="domcontentloaded")
        assert response is not None, "Navigation completed without an HTTP response"
        headers = await response.all_headers()

    missing_headers = [
        f"{header_name} ({description})"
        for header_name, description in required_headers.items()
        if header_name not in headers
    ]
    test_diagnostics.record(
        "security_headers_audit",
        route="/",
        missing_headers=missing_headers,
        present_headers=sorted(
            header_name for header_name in required_headers if header_name in headers
        ),
    )
    assert not missing_headers, f"Missing defense headers: {missing_headers}"
