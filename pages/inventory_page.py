"""SauceDemo inventory page object."""

from __future__ import annotations

from playwright.async_api import expect

from pages.base_page import BasePage


class InventoryPage(BasePage):
    """Model product browsing and cart actions on SauceDemo."""

    inventory_container = "inventory-container"
    cart_link = "shopping-cart-link"
    cart_badge = "shopping-cart-badge"

    @staticmethod
    def _product_slug(product_name: str) -> str:
        """Convert a SauceDemo product name to its selector suffix."""
        return product_name.strip().lower().replace(" ", "-")

    async def expect_loaded(self) -> None:
        """Assert that the inventory view is ready for interaction."""
        await self.expect_data_test_visible(self.inventory_container)

    async def add_product_to_cart(self, product_name: str) -> None:
        """Add a named product to the cart."""
        await self.click_data_test(f"add-to-cart-{self._product_slug(product_name)}")

    async def expect_cart_count(self, count: int) -> None:
        """Assert the number displayed on the cart badge."""
        await expect(self.data_test(self.cart_badge)).to_have_text(str(count))

    async def open_cart(self) -> None:
        """Open the shopping cart."""
        await self.click_data_test(self.cart_link)
