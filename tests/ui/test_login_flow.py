from __future__ import annotations

import pytest

from coverage_agent.decorators import covers
from pages.login_page import LoginPage


@pytest.mark.ui
@pytest.mark.asyncio
@covers(type="ui", target="login-submit", priority="high", template="InteractionTemplate")
@covers(type="ui", target="login-banner", priority="high", template="ComponentVisibilityTemplate")
async def test_login_page_smoke(page_factory):
    """Smoke test the login page object against a minimal DOM."""
    async with page_factory() as page:
        login = LoginPage(page)
        await page.set_content(
            """
            <button data-testid='login-submit'>Sign in</button>
            <input data-testid='login-username' />
            <input data-testid='login-password' />
            <div data-testid='login-banner'>Welcome</div>
            """
        )
        await login.login("demo", "demo")
        await login.expect_banner("Welcome")
