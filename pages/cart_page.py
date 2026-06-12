"""SauceDemo cart page object."""

from __future__ import annotations

from playwright.async_api import expect

from pages.base_page import BasePage


class CartPage(BasePage):
    """Model cart verification and checkout navigation."""

    cart_item = "inventory-item"
    item_name = "inventory-item-name"
    checkout_button = "checkout"

    async def expect_product(self, product_name: str) -> None:
        """Assert that the cart contains the named product."""
        await expect(self.data_test(self.item_name).filter(has_text=product_name)).to_be_visible()

    async def expect_item_count(self, count: int) -> None:
        """Assert the total number of cart line items."""
        await expect(self.data_test(self.cart_item)).to_have_count(count)

    async def checkout(self) -> None:
        """Continue from the cart to checkout."""
        await self.click_data_test(self.checkout_button)
