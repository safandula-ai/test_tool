from __future__ import annotations

from playwright.sync_api import Page, expect


class SyncSauceLoginPage:
    """Synchronous page object for the live SauceDemo login page."""

    def __init__(self, page: Page):
        self.page = page

    def data_test(self, value: str):
        return self.page.locator(f'[data-test="{value}"]')

    def open(self) -> None:
        self.page.goto("/")

    def login(self, username: str, password: str) -> None:
        self.data_test("username").fill(username)
        self.data_test("password").fill(password)
        self.data_test("login-button").click()

    def expect_inventory_loaded(self) -> None:
        expect(self.data_test("inventory-container")).to_be_visible()
