"""Advanced live tests for Automation Exercise."""

from __future__ import annotations

import httpx
import pytest

from api_clients.automation_exercise_client import AutomationExerciseClient, build_account_payload
from config.settings import ROOT
from coverage_agent.decorators import covers
from pages.automation_signup_page import AutomationSignupPage
from tests.websites.automationexercise_com.suite_config import BASE_URL
from tests.websites.helpers import require_live_target, resolve_target_url
from utils.visual_regression import assert_visual_match
from utils.test_diagnostics import TestDiagnosticRecorder, httpx_event_hooks


@pytest.mark.ui
@pytest.mark.hybrid
@pytest.mark.asyncio
@covers(type="api", target="POST /api/createAccount", priority="high", template="APIContractTemplate")
@covers(type="ui", target="signup-button", priority="high", template="InteractionTemplate")
async def test_api_created_email_is_rejected_by_ui(
    page_factory,
    pytestconfig,
    fake,
    settings,
    test_diagnostics: TestDiagnosticRecorder,
):
    """Create an account via API and verify duplicate signup through the UI."""
    require_live_target(pytestconfig, settings)
    base_url = resolve_target_url(
        pytestconfig,
        default_base_url=BASE_URL,
    )
    email = fake.unique.email()
    password = "StrongPassword123!"
    payload = build_account_payload("Hybrid User", email, password)

    async with httpx.AsyncClient(
        base_url=base_url,
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as http_client:
        api = AutomationExerciseClient(http_client)
        created = await api.create_account(payload)
        assert created["responseCode"] == 201

        try:
            async with page_factory(base_url) as page:
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
@covers(type="ui", target="signup-name", priority="high", template="FormValidationTemplate")
@covers(type="ui", target="signup-email", priority="high", template="FormValidationTemplate")
@covers(type="ui", target="signup-button", priority="high", template="InteractionTemplate")
async def test_signup_form_has_accessible_controls(page_factory, pytestconfig, settings):
    """Verify accessible names on the critical signup controls."""
    require_live_target(pytestconfig, settings)
    base_url = resolve_target_url(
        pytestconfig,
        default_base_url=BASE_URL,
    )
    async with page_factory(base_url) as page:
        signup = AutomationSignupPage(page)
        await signup.open()
        await signup.expect_signup_form_accessible()


@pytest.mark.ui
@pytest.mark.asyncio
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
async def test_login_fields_enforce_input_constraints(page_factory, pytestconfig, settings):
    """Verify required and malformed credential validation on the login form."""
    require_live_target(pytestconfig, settings)
    base_url = resolve_target_url(
        pytestconfig,
        default_base_url=BASE_URL,
    )
    async with page_factory(base_url) as page:
        signup = AutomationSignupPage(page)
        await signup.open()
        await signup.expect_login_input_constraints()


@pytest.mark.ui
@pytest.mark.visual
@pytest.mark.asyncio
@covers(type="visual", target="signup-form", priority="medium", template="ComponentVisibilityTemplate")
async def test_signup_form_visual_regression(page_factory, pytestconfig, settings):
    """Compare the signup form with its stored visual baseline."""
    require_live_target(pytestconfig, settings)
    base_url = resolve_target_url(
        pytestconfig,
        default_base_url=BASE_URL,
    )
    baseline = ROOT / "data" / "visual" / "automation-signup-form.png"
    if not baseline.exists() and not settings.update_visual_baselines:
        pytest.skip("Set UPDATE_VISUAL_BASELINES=true once to create the baseline")

    async with page_factory(base_url) as page:
        await page.goto("/login")
        signup_form = page.locator(".signup-form")
        await assert_visual_match(
            signup_form,
            baseline=baseline,
            actual=settings.screenshot_dir / "automation-signup-form.actual.png",
            max_changed_pixel_ratio=0.01,
            update_baseline=settings.update_visual_baselines,
        )
