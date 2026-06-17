"""Automation Exercise-specific page objects and selector helpers."""

from __future__ import annotations

from playwright.async_api import Locator, Page, expect

from tests.websites.helpers import dismiss_consent_if_present


class AutomationExercisePage:
    """Base page object for Automation Exercise selectors and shared flows."""

    def __init__(self, page: Page):
        self.page = page

    def data_qa(self, value: str) -> Locator:
        """Return a locator backed by Automation Exercise's `data-qa` attribute."""
        return self.page.locator(f'[data-qa="{value}"]')

    def text(self, value: str, exact: bool = False) -> Locator:
        """Return a text locator for visible content assertions."""
        return self.page.get_by_text(value, exact=exact)

    async def fill_data_qa(self, value: str, text: str) -> None:
        """Fill a field selected by `data-qa`."""
        await self.data_qa(value).fill(text)

    async def click_data_qa(self, value: str) -> None:
        """Click an element selected by `data-qa`."""
        await self.data_qa(value).click()

    async def dismiss_consent_dialog(self) -> None:
        """Accept the optional consent dialog that can block form controls."""
        await dismiss_consent_if_present(
            self.page,
            root_selector=".fc-dialog-container",
            accept_selector=".fc-cta-consent, button:has-text('Consent')",
        )


class AutomationSignupPage(AutomationExercisePage):
    """Model signup actions and duplicate-email validation."""

    signup_name = "signup-name"
    signup_email = "signup-email"
    signup_button = "signup-button"
    login_email = "login-email"
    login_password = "login-password"

    async def open(self) -> None:
        """Open the signup and login page."""
        await self.page.goto("/login")
        await self.dismiss_consent_dialog()

    async def signup(self, name: str, email: str) -> None:
        """Submit the first signup step."""
        await self.fill_data_qa(self.signup_name, name)
        await self.fill_data_qa(self.signup_email, email)
        await self.click_data_qa(self.signup_button)

    async def expect_duplicate_email_error(self) -> None:
        """Assert the documented duplicate-email validation message."""
        await expect(self.text("Email Address already exist!", exact=True)).to_be_visible()

    async def expect_signup_form_accessible(self) -> None:
        """Assert that critical signup controls expose accessible names."""
        await expect(self.page.get_by_role("textbox", name="Name")).to_be_visible()
        await expect(self.page.get_by_role("textbox", name="Email Address").last).to_be_visible()
        await expect(self.page.get_by_role("button", name="Signup")).to_be_visible()

    async def expect_login_input_constraints(self) -> None:
        """Assert browser-level validation constraints on login credentials."""
        email = self.data_qa(self.login_email)
        password = self.data_qa(self.login_password)

        await expect(email).to_have_attribute("type", "email")
        await expect(email).to_have_attribute("required", "")
        await expect(password).to_have_attribute("type", "password")
        await expect(password).to_have_attribute("required", "")

        await email.fill("not-an-email")
        assert await email.evaluate("element => !element.checkValidity()")
        assert await password.evaluate("element => !element.checkValidity()")
