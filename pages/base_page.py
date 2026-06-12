from __future__ import annotations

from playwright.async_api import Locator, Page, expect


class BasePage:
    """Asynchronous Playwright page object base for the main UI suite."""

    def __init__(self, page: Page):
        """Store the active Playwright page handle."""
        self.page = page

    def test_id(self, value: str) -> Locator:
        """Return a resilient locator backed by `data-testid`."""
        return self.page.get_by_test_id(value)

    def data_test(self, value: str) -> Locator:
        """Return a locator backed by SauceDemo's `data-test` attribute."""
        return self.page.locator(f'[data-test="{value}"]')

    def data_qa(self, value: str) -> Locator:
        """Return a locator backed by Automation Exercise's `data-qa` attribute."""
        return self.page.locator(f'[data-qa="{value}"]')

    def text(self, value: str, exact: bool = False) -> Locator:
        """Return a text locator for visible content assertions."""
        return self.page.get_by_text(value, exact=exact)

    async def fill_test_id(self, value: str, text: str) -> None:
        """Fill a `data-testid` field with the provided text."""
        await self.test_id(value).fill(text)

    async def click_test_id(self, value: str) -> None:
        """Click a `data-testid` element."""
        await self.test_id(value).click()

    async def fill_data_test(self, value: str, text: str) -> None:
        """Fill a field selected by `data-test`."""
        await self.data_test(value).fill(text)

    async def click_data_test(self, value: str) -> None:
        """Click an element selected by `data-test`."""
        await self.data_test(value).click()

    async def fill_data_qa(self, value: str, text: str) -> None:
        """Fill a field selected by `data-qa`."""
        await self.data_qa(value).fill(text)

    async def click_data_qa(self, value: str) -> None:
        """Click an element selected by `data-qa`."""
        await self.data_qa(value).click()

    async def expect_data_test_visible(self, value: str) -> None:
        """Assert that a `data-test` element is visible."""
        await expect(self.data_test(value)).to_be_visible()

    async def expect_url(self, path_or_pattern: str) -> None:
        """Assert the current URL using Playwright's auto-retrying assertion."""
        await expect(self.page).to_have_url(path_or_pattern)
