"""SauceDemo checkout page object."""

from __future__ import annotations

from playwright.async_api import expect

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """Model customer details, order review, and completion."""

    first_name_input = "firstName"
    last_name_input = "lastName"
    postal_code_input = "postalCode"
    continue_button = "continue"
    finish_button = "finish"
    complete_header = "complete-header"

    async def enter_customer_details(self, first_name: str, last_name: str, postal_code: str) -> None:
        """Fill customer details and continue to order review."""
        await self.fill_data_test(self.first_name_input, first_name)
        await self.fill_data_test(self.last_name_input, last_name)
        await self.fill_data_test(self.postal_code_input, postal_code)
        await self.click_data_test(self.continue_button)

    async def finish_order(self) -> None:
        """Confirm the reviewed order."""
        await self.click_data_test(self.finish_button)

    async def expect_complete(self) -> None:
        """Assert that SauceDemo reports a completed order."""
        await expect(self.data_test(self.complete_header)).to_have_text("Thank you for your order!")
