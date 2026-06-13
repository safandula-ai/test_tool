"""Automation Exercise signup page object."""

from __future__ import annotations

from playwright.async_api import expect

from pages.base_page import BasePage


class AutomationSignupPage(BasePage):
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

    async def dismiss_consent_dialog(self) -> None:
        """Accept the optional consent dialog that can block form controls."""
        consent = self.page.locator(".fc-cta-consent, button:has-text('Consent')").first
        if await consent.is_visible():
            await consent.click()

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
