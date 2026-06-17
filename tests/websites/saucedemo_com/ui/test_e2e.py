"""Live SauceDemo end-to-end tests."""

from __future__ import annotations

import pytest

from coverage_agent.decorators import covers
from tests.websites.saucedemo_com.helpers import CartPage, CheckoutPage, InventoryPage, SauceLoginPage
from tests.websites.saucedemo_com.suite_config import BASE_URL, SAUCE_PASSWORD, SAUCE_USERNAME


pytestmark = [
    pytest.mark.ui,
    pytest.mark.e2e,
    pytest.mark.asyncio,
]


@covers(type="ui", target="login-button", priority="critical", template="InteractionTemplate")
@covers(type="ui", target="inventory-container", priority="high", template="ComponentVisibilityTemplate")
@covers(type="ui", target="shopping-cart-link", priority="high", template="InteractionTemplate")
@covers(type="ui", target="checkout", priority="critical", template="InteractionTemplate")
@covers(type="ui", target="finish", priority="critical", template="InteractionTemplate")
@covers(type="ui", target="complete-header", priority="critical", template="ComponentVisibilityTemplate")
async def test_standard_user_can_complete_purchase(page_factory, test_diagnostics):
    """Verify login, cart state, and the complete purchase happy path."""
    base_url = BASE_URL
    async with page_factory(base_url) as page:
        login = SauceLoginPage(page)
        inventory = InventoryPage(page)
        cart = CartPage(page)
        checkout = CheckoutPage(page)

        test_diagnostics.record("suite_target", base_url=base_url, suite="saucedemo_com")
        test_diagnostics.record("journey_step", step="open_login")
        await login.open()
        test_diagnostics.record("journey_step", step="login_standard_user", username=SAUCE_USERNAME)
        await login.login(SAUCE_USERNAME, SAUCE_PASSWORD)
        test_diagnostics.record("journey_step", step="inventory_loaded")
        await inventory.expect_loaded()
        test_diagnostics.record("journey_step", step="add_product_to_cart", product="Sauce Labs Backpack")
        await inventory.add_product_to_cart("Sauce Labs Backpack")
        await inventory.expect_cart_count(1)
        test_diagnostics.record("journey_step", step="open_cart")
        await inventory.open_cart()
        await cart.expect_product("Sauce Labs Backpack")
        await cart.expect_item_count(1)
        test_diagnostics.record("journey_step", step="checkout_start")
        await cart.checkout()
        test_diagnostics.record(
            "journey_step",
            step="enter_customer_details",
            first_name="Test",
            last_name="User",
            postal_code="00-001",
        )
        await checkout.enter_customer_details("Test", "User", "00-001")
        test_diagnostics.record("journey_step", step="finish_order")
        await checkout.finish_order()
        await checkout.expect_complete()
        test_diagnostics.record(
            "journey_complete",
            final_url=page.url,
            page_title=await page.title(),
        )


@covers(type="ui", target="login-button", priority="high", template="InteractionTemplate")
@covers(type="ui", target="error", priority="high", template="ComponentVisibilityTemplate")
async def test_locked_user_sees_login_error(page_factory, test_diagnostics):
    """Verify the locked-user negative login path."""
    base_url = BASE_URL
    async with page_factory(base_url) as page:
        login = SauceLoginPage(page)
        test_diagnostics.record("suite_target", base_url=base_url, suite="saucedemo_com")
        test_diagnostics.record("journey_step", step="open_login")
        await login.open()
        test_diagnostics.record("journey_step", step="login_locked_user", username="locked_out_user")
        await login.login("locked_out_user", SAUCE_PASSWORD)
        await login.expect_login_error("Sorry, this user has been locked out")
        test_diagnostics.record(
            "journey_complete",
            final_url=page.url,
            page_title=await page.title(),
            expected_error="Sorry, this user has been locked out",
        )
