"""Advanced live tests for Automation Exercise."""

from __future__ import annotations

import httpx
import pytest

from api_clients.automation_exercise_client import AutomationExerciseClient, build_account_payload
from config.settings import ROOT, get_settings
from coverage_agent.decorators import covers
from pages.automation_signup_page import AutomationSignupPage
from tests.websites.automationexercise_com.suite_config import BASE_URL
from utils.visual_regression import assert_visual_match
from utils.test_diagnostics import TestDiagnosticRecorder, httpx_event_hooks


LIVE_ONLY = pytest.mark.skipif(
    not get_settings().run_live_tests,
    reason="Set RUN_LIVE_TESTS=true to call Automation Exercise",
)


@pytest.mark.ui
@pytest.mark.hybrid
@pytest.mark.asyncio
@LIVE_ONLY
@covers(type="api", target="POST /api/createAccount", priority="high", template="APIContractTemplate")
@covers(type="ui", target="signup-button", priority="high", template="InteractionTemplate")
async def test_api_created_email_is_rejected_by_ui(
    page_factory,
    fake,
    settings,
    test_diagnostics: TestDiagnosticRecorder,
):
    """Create an account via API and verify duplicate signup through the UI."""
    email = fake.unique.email()
    password = "StrongPassword123!"
    payload = build_account_payload("Hybrid User", email, password)

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as http_client:
        api = AutomationExerciseClient(http_client)
        created = await api.create_account(payload)
        assert created["responseCode"] == 201

        try:
            async with page_factory(BASE_URL) as page:
                signup = AutomationSignupPage(page)
                await signup.open()
                await signup.signup(payload["name"], email)
                await signup.expect_duplicate_email_error()
        finally:
            deleted = await api.delete_account(email, password)
            assert deleted["responseCode"] == 200


@pytest.mark.ui
@pytest.mark.a11y
@pytest.mark.asyncio
@LIVE_ONLY
@covers(type="ui", target="signup-name", priority="high", template="FormValidationTemplate")
@covers(type="ui", target="signup-email", priority="high", template="FormValidationTemplate")
@covers(type="ui", target="signup-button", priority="high", template="InteractionTemplate")
async def test_signup_form_has_accessible_controls(page_factory, settings):
    """Verify accessible names on the critical signup controls."""
    async with page_factory(BASE_URL) as page:
        signup = AutomationSignupPage(page)
        await signup.open()
        await signup.expect_signup_form_accessible()


@pytest.mark.ui
@pytest.mark.asyncio
@LIVE_ONLY
@covers(
    type="ui",
    target="login-email",
    priority="high",
    template="InputValidationTemplate",
    page="/login",
    feature="feature:authentication",
)
@covers(
    type="ui",
    target="login-password",
    priority="high",
    template="InputValidationTemplate",
    page="/login",
    feature="feature:authentication",
)
async def test_login_fields_enforce_input_constraints(page_factory, settings):
    """Verify required and malformed credential validation on the login form."""
    async with page_factory(BASE_URL) as page:
        signup = AutomationSignupPage(page)
        await signup.open()
        await signup.expect_login_input_constraints()


@pytest.mark.ui
@pytest.mark.visual
@pytest.mark.asyncio
@LIVE_ONLY
@covers(type="visual", target="signup-form", priority="medium", template="ComponentVisibilityTemplate")
async def test_signup_form_visual_regression(page_factory, settings):
    """Compare the signup form with its stored visual baseline."""
    baseline = ROOT / "data" / "visual" / "automation-signup-form.png"
    if not baseline.exists() and not settings.update_visual_baselines:
        pytest.skip("Set UPDATE_VISUAL_BASELINES=true once to create the baseline")

    async with page_factory(BASE_URL) as page:
        await page.goto("/login")
        signup_form = page.locator(".signup-form")
        await assert_visual_match(
            signup_form,
            baseline=baseline,
            actual=settings.screenshot_dir / "automation-signup-form.actual.png",
            max_changed_pixel_ratio=0.01,
            update_baseline=settings.update_visual_baselines,
        )
