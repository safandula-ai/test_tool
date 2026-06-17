"""Live SauceDemo BDD login scenario."""

from __future__ import annotations

import pytest

pytest.importorskip("pytest_bdd")

from pytest_bdd import given, scenario, then, when

from coverage_agent.decorators import covers
from tests.websites.saucedemo_com.bdd.helpers import SyncSauceLoginPage
from tests.websites.saucedemo_com.suite_config import BASE_URL, SAUCE_PASSWORD, SAUCE_USERNAME
from utils.test_diagnostics import TestDiagnosticRecorder


@pytest.mark.bdd
@scenario("features/login.feature", "standard user can sign in")
@covers(
    type="ui",
    target="login-button",
    priority="critical",
    template="InteractionTemplate",
    page="/",
    feature="feature:authentication",
)
@covers(
    type="ui",
    target="inventory-container",
    priority="high",
    template="ComponentVisibilityTemplate",
    page="/inventory.html",
    feature="feature:authentication",
)
def test_standard_user_can_sign_in():
    """Bind the live SauceDemo login scenario to pytest."""
    pass


@given("the SauceDemo login page is open", target_fixture="login_page")
def login_page(sync_page, test_diagnostics: TestDiagnosticRecorder):
    """Open the real SauceDemo login page and expose a sync page object."""
    page = SyncSauceLoginPage(sync_page)
    test_diagnostics.record(
        "test_surface",
        mode="live_page",
        url=BASE_URL,
        payload={"suite": "saucedemo_com"},
    )
    test_diagnostics.record("journey_step", step="open_login", payload={"url": BASE_URL})
    page.open()
    return page


@when("the standard SauceDemo user signs in")
def sign_in(login_page: SyncSauceLoginPage, test_diagnostics: TestDiagnosticRecorder):
    """Submit the standard SauceDemo credentials."""
    test_diagnostics.record(
        "journey_step",
        step="submit_login",
        payload={"username": SAUCE_USERNAME},
    )
    login_page.login(SAUCE_USERNAME, SAUCE_PASSWORD)


@then("the inventory page is shown")
def inventory_page(login_page: SyncSauceLoginPage, test_diagnostics: TestDiagnosticRecorder):
    """Verify that login reached the live inventory page."""
    test_diagnostics.record(
        "assertion",
        name="inventory_container_visible",
        payload={"expected_target": "inventory-container"},
    )
    login_page.expect_inventory_loaded()
