"""SauceDemo login page object."""

from __future__ import annotations

from playwright.async_api import expect

from pages.base_page import BasePage


class SauceLoginPage(BasePage):
    """Model login actions and validation for SauceDemo."""

    username_input = "username"
    password_input = "password"
    login_button = "login-button"
    error_message = "error"

    async def open(self) -> None:
        """Open the SauceDemo login page."""
        await self.page.goto("/")

    async def login(self, username: str, password: str) -> None:
        """Submit the supplied SauceDemo credentials."""
        await self.fill_data_test(self.username_input, username)
        await self.fill_data_test(self.password_input, password)
        await self.click_data_test(self.login_button)

    async def expect_login_error(self, message: str) -> None:
        """Assert that login failed with the expected message."""
        await expect(self.data_test(self.error_message)).to_contain_text(message)
