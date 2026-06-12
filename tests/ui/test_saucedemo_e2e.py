"""Live SauceDemo end-to-end tests."""

from __future__ import annotations

import pytest

from config.settings import get_settings
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.sauce_login_page import SauceLoginPage


pytestmark = [
    pytest.mark.ui,
    pytest.mark.e2e,
    pytest.mark.asyncio,
    pytest.mark.skipif(not get_settings().run_live_tests, reason="Set RUN_LIVE_TESTS=true to call SauceDemo"),
]


async def test_standard_user_can_complete_purchase(page_factory, settings):
    """Verify login, cart state, and the complete purchase happy path."""
    async with page_factory() as page:
        login = SauceLoginPage(page)
        inventory = InventoryPage(page)
        cart = CartPage(page)
        checkout = CheckoutPage(page)

        await login.open()
        await login.login(settings.sauce_username, settings.sauce_password)
        await inventory.expect_loaded()
        await inventory.add_product_to_cart("Sauce Labs Backpack")
        await inventory.expect_cart_count(1)
        await inventory.open_cart()
        await cart.expect_product("Sauce Labs Backpack")
        await cart.expect_item_count(1)
        await cart.checkout()
        await checkout.enter_customer_details("Test", "User", "00-001")
        await checkout.finish_order()
        await checkout.expect_complete()


async def test_locked_user_sees_login_error(page_factory, settings):
    """Verify the locked-user negative login path."""
    async with page_factory() as page:
        login = SauceLoginPage(page)
        await login.open()
        await login.login("locked_out_user", settings.sauce_password)
        await login.expect_login_error("Sorry, this user has been locked out")
