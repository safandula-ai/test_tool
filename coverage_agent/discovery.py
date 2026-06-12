"""Playwright-based UI target and API endpoint discovery."""

from __future__ import annotations

import asyncio
import json
import random
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import Page, Request, async_playwright


IGNORED_NETWORK_TOKENS = ("analytics", "telemetry", "google-analytics")
TARGET_ATTRIBUTES = ("data-testid", "data-test", "data-qa")


class PlaywrightDiscoveryEngine:
    """Discover stable UI selectors and same-site API requests for a route."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.discovered_ui_elements: set[str] = set()
        self.discovered_api_endpoints: set[str] = set()

    async def handle_cookie_banner(self, page: Page) -> None:
        """Dismiss a common consent banner when one is visible."""
        selectors = (
            "button:has-text('Accept All')",
            "button:has-text('Accept')",
            "button:has-text('Consent')",
            "button:has-text('Zgadzam się')",
            "[aria-label='Accept cookies']",
            "#cookie-accept-btn",
        )
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=750):
                    await element.click()
                    return
            except Exception:
                continue

    async def monitor_network(self, request: Request) -> None:
        """Record relevant API requests as ``METHOD /path`` signatures."""
        signature = self.endpoint_signature(request.method, request.url)
        if signature:
            self.discovered_api_endpoints.add(signature)

    def endpoint_signature(self, method: str, url: str) -> str | None:
        """Normalize an in-scope API URL into a stable endpoint signature."""
        parsed = urlsplit(url)
        base = urlsplit(self.base_url)
        if parsed.netloc != base.netloc or "/api/" not in parsed.path:
            return None
        if any(token in url.lower() for token in IGNORED_NETWORK_TOKENS):
            return None
        return f"{method.upper()} {parsed.path}"

    async def scrape_page(
        self,
        target_path: str,
        *,
        auth_state_path: str | Path | None = None,
        save_state_path: str | Path | None = None,
        headless: bool = True,
    ) -> dict[str, object]:
        """Visit a route and return its discovered application manifest."""
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=headless)
            context_options: dict[str, object] = {
                "locale": "en-US",
                "user_agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
                ),
                "viewport": {"width": 1280, "height": 720},
            }
            if auth_state_path is not None:
                context_options["storage_state"] = str(auth_state_path)
            context = await browser.new_context(**context_options)
            await context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            page = await context.new_page()
            page.on("request", lambda request: asyncio.create_task(self.monitor_network(request)))
            try:
                await page.goto(f"{self.base_url}/{target_path.lstrip('/')}", wait_until="networkidle")
                await self.handle_cookie_banner(page)
                await page.wait_for_timeout(random.randint(150, 450))
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                for attribute in TARGET_ATTRIBUTES:
                    for element in await page.query_selector_all(f"[{attribute}]"):
                        value = await element.get_attribute(attribute)
                        if value:
                            self.discovered_ui_elements.add(value)
                if save_state_path is not None:
                    await context.storage_state(path=str(save_state_path))
            finally:
                await context.close()
                await browser.close()
        return self.application_manifest(target_path)

    def application_manifest(self, page: str) -> dict[str, object]:
        """Build a deterministic application map."""
        normalized_page = "/" + page.lstrip("/")
        return {
            "page": normalized_page,
            "discovered_ui_elements": sorted(self.discovered_ui_elements),
            "discovered_api_endpoints": sorted(self.discovered_api_endpoints),
        }

    def write_application_manifest(self, page: str, output_file: str | Path) -> None:
        """Write the current application map to JSON."""
        destination = Path(output_file)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(self.application_manifest(page), indent=2) + "\n",
            encoding="utf-8",
        )
