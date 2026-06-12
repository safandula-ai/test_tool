from __future__ import annotations

from playwright.async_api import expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Asynchronous login page object for the main UI suite."""

    username = "login-username"
    password = "login-password"
    submit = "login-submit"
    banner = "login-banner"

    async def open(self) -> None:
        """Open the application root."""
        await self.page.goto("/")

    async def login(self, username: str, password: str) -> None:
        """Submit credentials through the login form."""
        await self.fill_test_id(self.username, username)
        await self.fill_test_id(self.password, password)
        await self.click_test_id(self.submit)

    async def expect_banner(self, text: str) -> None:
        """Assert the expected success banner text."""
        await expect(self.test_id(self.banner)).to_have_text(text)
