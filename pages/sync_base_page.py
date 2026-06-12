from __future__ import annotations

from playwright.sync_api import Page


class SyncBasePage:
    """Synchronous Playwright page object base for readable BDD steps."""

    def __init__(self, page: Page):
        """Store the active Playwright page handle."""
        self.page = page

    def test_id(self, value: str):
        """Return a resilient locator backed by `data-testid`."""
        return self.page.get_by_test_id(value)

    def text(self, value: str):
        """Return a text locator for visible content assertions."""
        return self.page.get_by_text(value)

    def fill_test_id(self, value: str, text: str) -> None:
        """Fill a `data-testid` field with the provided text."""
        self.test_id(value).fill(text)

    def click_test_id(self, value: str) -> None:
        """Click a `data-testid` element."""
        self.test_id(value).click()
