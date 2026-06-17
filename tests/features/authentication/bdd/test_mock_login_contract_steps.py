from __future__ import annotations

import pytest

pytest.importorskip("pytest_bdd")

from pytest_bdd import given, scenario, then, when

from coverage_agent.decorators import covers
from pages.sync_login_page import SyncLoginPage
from utils.test_diagnostics import TestDiagnosticRecorder


MOCK_LOGIN_FORM_HTML = """
<button data-testid='login-submit'>Sign in</button>
<input data-testid='login-username' />
<input data-testid='login-password' />
<div data-testid='login-banner'>Welcome</div>
""".strip()


@pytest.mark.bdd
@scenario(
    "features/mock_login_contract.feature",
    "demo credentials submit through the mock login form",
)
@covers(
    type="ui",
    target="login-submit",
    priority="high",
    template="InteractionTemplate",
    page="mock://login-form",
    feature="feature:local-page-contracts",
)
@covers(
    type="ui",
    target="login-banner",
    priority="high",
    template="ComponentVisibilityTemplate",
    page="mock://login-form",
    feature="feature:local-page-contracts",
)
def test_mock_login_form_contract():
    """Bind the mocked login page-object contract scenario to pytest."""
    pass


@given("the mock login form is rendered", target_fixture="login_page")
def login_page(sync_page, test_diagnostics: TestDiagnosticRecorder):
    """Render a minimal login DOM and expose the page object."""
    page = SyncLoginPage(sync_page)
    sync_page.set_content(MOCK_LOGIN_FORM_HTML)
    test_diagnostics.record(
        "journey_step",
        step="render_mock_login_form",
        payload={
            "page_object": "SyncLoginPage",
            "selector_targets": {
                "username": page.username,
                "password": page.password,
                "submit": page.submit,
                "banner": page.banner,
            },
        },
    )
    test_diagnostics.record(
        "test_surface",
        mode="mock_dom",
        url="mock://login-form",
        payload={
            "html": MOCK_LOGIN_FORM_HTML,
            "selectors": [
                "login-submit",
                "login-username",
                "login-password",
                "login-banner",
            ],
        },
    )
    return page


@when('the user signs in with username "demo" and password "demo"')
def sign_in(login_page, test_diagnostics: TestDiagnosticRecorder):
    """Submit the demo credentials through the page object."""
    test_diagnostics.record(
        "journey_step",
        step="fill_mock_login_fields",
        payload={
            "username_selector": login_page.username,
            "password_selector": login_page.password,
            "username": "demo",
            "password": "demo",
        },
    )
    test_diagnostics.record(
        "interaction",
        action="mock_login_submit",
        payload={
            "submit_selector": login_page.submit,
            "username": "demo",
            "password": "demo",
        },
    )
    login_page.login("demo", "demo")
    test_diagnostics.record(
        "journey_step",
        step="mock_login_submitted",
        payload={"submit_selector": login_page.submit},
    )


@then('the mock welcome banner should say "Welcome"')
def welcome_banner(login_page, test_diagnostics: TestDiagnosticRecorder):
    """Check that the success banner contains the expected text."""
    observed_banner_text = login_page.test_id(login_page.banner).text_content() or ""
    test_diagnostics.record(
        "assertion",
        name="mock_welcome_banner_text",
        payload={
            "banner_selector": login_page.banner,
            "expected_text": "Welcome",
            "observed_text": observed_banner_text.strip(),
        },
    )
    login_page.expect_banner("Welcome")
