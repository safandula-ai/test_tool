"""Generated coverage tests. Regenerate with ``coverage_agent scaffold-gaps``."""

from __future__ import annotations

import pytest
from playwright.async_api import expect

from coverage_agent.decorators import covers


DEFAULT_BASE_URL = 'https://www.saucedemo.com'

pytestmark = [
    pytest.mark.ui,
    pytest.mark.asyncio,
]


def _target(page, name: str):
    escaped = name.replace('"', '\"')
    return page.locator(
        f'[data-testid="{escaped}"], [data-test="{escaped}"], [data-qa="{escaped}"]'
    ).first


async def _assert_input_validation(target) -> None:
    await expect(target).to_be_visible()
    await expect(target).to_be_editable()
    input_type = (await target.get_attribute("type") or "text").lower()
    await target.fill("not-a-valid-value")
    if input_type in {"email", "url", "number"}:
        assert not await target.evaluate("element => element.checkValidity()")
    else:
        assert await target.input_value() == "not-a-valid-value"


async def _assert_interaction(target) -> None:
    await expect(target).to_be_visible()
    await expect(target).to_be_enabled()


@covers(type="ui", target="login-button", priority="high", template="InteractionTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_login_button(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "login-button")
        await _assert_interaction(target)


@covers(type="ui", target="login-container", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_login_container(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "login-container")
        await expect(target).to_be_visible()


@covers(type="ui", target="login-credentials", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_login_credentials(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "login-credentials")
        await expect(target).to_be_visible()


@covers(type="ui",
        target="login-credentials-container",
        priority="high",
        template="ComponentVisibilityTemplate",
        page='/',
        feature='feature:generated-gap-coverage',
        presence="deterministic")
async def test_generated_ui_login_credentials_container(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "login-credentials-container")
        await expect(target).to_be_visible()


@covers(type="ui", target="password", priority="high", template="InputValidationTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_password(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "password")
        await _assert_input_validation(target)


@covers(type="ui", target="username", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_username(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "username")
        await expect(target).to_be_visible()
