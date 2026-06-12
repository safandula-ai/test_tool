from __future__ import annotations

from playwright.sync_api import expect

from pages.sync_base_page import SyncBasePage


class SyncLoginPage(SyncBasePage):
    """Page object for the login experience used by BDD scenarios."""

    username = "login-username"
    password = "login-password"
    submit = "login-submit"
    banner = "login-banner"

    def open(self) -> None:
        """Open the application root."""
        self.page.goto("/")

    def login(self, username: str, password: str) -> None:
        """Submit credentials through the login form."""
        self.fill_test_id(self.username, username)
        self.fill_test_id(self.password, password)
        self.click_test_id(self.submit)

    def expect_banner(self, text: str) -> None:
        """Assert the expected success banner text."""
        expect(self.test_id(self.banner)).to_have_text(text)
