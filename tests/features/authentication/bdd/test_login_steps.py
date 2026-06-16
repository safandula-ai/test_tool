from __future__ import annotations

import pytest

pytest.importorskip("pytest_bdd")

from pytest_bdd import given, scenario, then, when

from coverage_agent.decorators import covers
from pages.sync_login_page import SyncLoginPage


@pytest.mark.bdd
@scenario("features/login.feature", "successful login")
@covers(
    type="ui",
    target="login-submit",
    priority="high",
    template="InteractionTemplate",
    page="/login",
    feature="feature:authentication",
)
@covers(
    type="ui",
    target="login-banner",
    priority="high",
    template="ComponentVisibilityTemplate",
    page="/login",
    feature="feature:authentication",
)
def test_successful_login():
    """Bind the readable login scenario to a pytest test."""
    pass


@given("the login form is visible", target_fixture="login_page")
def login_page(sync_page):
    """Render a minimal login DOM and expose the page object."""
    page = SyncLoginPage(sync_page)
    sync_page.set_content(
        """
        <button data-testid='login-submit'>Sign in</button>
        <input data-testid='login-username' />
        <input data-testid='login-password' />
        <div data-testid='login-banner'>Welcome</div>
        """
    )
    return page


@when('the user signs in with username "demo" and password "demo"')
def sign_in(login_page):
    """Submit the demo credentials through the page object."""
    login_page.login("demo", "demo")


@then('the welcome banner should say "Welcome"')
def welcome_banner(login_page):
    """Check that the success banner contains the expected text."""
    login_page.expect_banner("Welcome")
