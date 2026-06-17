"""SauceDemo-specific page objects and selector helpers."""

from __future__ import annotations

from playwright.async_api import Locator, Page, expect


class SauceDemoPage:
    """Base page object for SauceDemo selectors and common assertions."""

    def __init__(self, page: Page):
        self.page = page

    def data_test(self, value: str) -> Locator:
        """Return a locator backed by SauceDemo's `data-test` attribute."""
        return self.page.locator(f'[data-test="{value}"]')

    async def fill_data_test(self, value: str, text: str) -> None:
        """Fill a field selected by `data-test`."""
        await self.data_test(value).fill(text)

    async def click_data_test(self, value: str) -> None:
        """Click an element selected by `data-test`."""
        await self.data_test(value).click()

    async def expect_data_test_visible(self, value: str) -> None:
        """Assert that a `data-test` element is visible."""
        await expect(self.data_test(value)).to_be_visible()


class SauceLoginPage(SauceDemoPage):
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


class InventoryPage(SauceDemoPage):
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


class CartPage(SauceDemoPage):
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


class CheckoutPage(SauceDemoPage):
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
