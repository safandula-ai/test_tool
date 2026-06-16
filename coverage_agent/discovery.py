"""Playwright-based UI target and API endpoint discovery."""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from playwright.async_api import Page, Request, TimeoutError as PlaywrightTimeoutError, async_playwright
from playwright_stealth import Stealth

from config.settings import ROOT, get_settings
from .plugins import get_scraper


IGNORED_NETWORK_TOKENS = ("analytics", "telemetry", "google-analytics")
TARGET_ATTRIBUTES = ("data-testid", "data-test", "data-qa")
SECURITY_CHALLENGE_SELECTORS = (
    "text=Checking if the site connection is secure",
    "text=/weryfikacj.*zabezpiecze/i",
    "#challenge-running",
    "iframe[src*='challenges']",
)
DOCUMENTATION_SOURCES_ROOT = ROOT / "coverage_agent" / "plugins" / "documentation_sources"


class PlaywrightDiscoveryEngine:
    """Discover stable UI selectors and same-site API requests for a route."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.discovered_ui_elements: set[str] = set()
        self.ui_element_details: dict[str, dict[str, object]] = {}
        self.discovered_api_endpoints: list[dict[str, str]] = []
        self.ui_element_presence: dict[str, str] = {}
        self.security_challenge_status = "not_detected"
        self.security_challenge_selector: str | None = None
        self.discovery_mode = "live_page"
        self.settings = get_settings()
        self.scraper = get_scraper(base_url)

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

    async def handle_security_challenges(
        self,
        page: Page,
        *,
        timeout_ms: int = 15_000,
    ) -> bool:
        """Wait for a detected verification wall to detach within a bounded timeout."""
        if timeout_ms <= 0:
            raise ValueError("Security challenge timeout must be positive")

        detected_selector = None
        for selector in SECURITY_CHALLENGE_SELECTORS:
            try:
                if await page.locator(selector).count() > 0:
                    detected_selector = selector
                    break
            except Exception:
                continue

        if detected_selector is None:
            self.security_challenge_status = "not_detected"
            self.security_challenge_selector = None
            return True

        self.security_challenge_status = "detected"
        self.security_challenge_selector = detected_selector
        try:
            await page.wait_for_selector(
                detected_selector,
                state="detached",
                timeout=timeout_ms,
            )
        except PlaywrightTimeoutError:
            self.security_challenge_status = "unresolved"
            return False

        self.security_challenge_status = "cleared"
        await page.wait_for_timeout(1_000)
        return True

    async def monitor_network(self, request: Request) -> None:
        """Record relevant API requests as ``METHOD /path`` signatures."""
        signature = self.endpoint_signature(request.method, request.url)
        if signature:
            if signature not in self.discovered_api_endpoints:
                self.discovered_api_endpoints.append(signature)

    def endpoint_signature(self, method: str, url: str) -> dict[str, str] | None:
        """Normalize an in-scope API URL into a stable endpoint signature."""
        parsed = urlsplit(url)
        base = urlsplit(self.base_url)
        if parsed.netloc != base.netloc or "/api/" not in parsed.path:
            return None
        if any(token in url.lower() for token in IGNORED_NETWORK_TOKENS):
            return None
        return {"method": method.upper(), "path": parsed.path}

    def documentation_source_path(self, file_name: str) -> Path:
        """Resolve a documentation source file inside the plugin source directory."""
        root = DOCUMENTATION_SOURCES_ROOT.resolve()
        candidate = (root / file_name).resolve()
        if root not in candidate.parents and candidate != root:
            raise ValueError("Documentation source must be inside coverage_agent/plugins/documentation_sources")
        if not candidate.is_file():
            raise FileNotFoundError(f"Documentation source not found: {candidate.name}")
        return candidate

    def documentation_source_page(self, file_name: str) -> str:
        """Build a stable manifest page identifier for documentation-backed discovery."""
        return f"/documentation_sources/{Path(file_name).name}"

    async def _fetch_asset_sha256(self, url: str) -> str | None:
        """Fetch an asset and return a stable content hash."""
        if not url.startswith(("http://", "https://")):
            return None
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=self.settings.http_timeout,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
        except Exception:
            return None
        return hashlib.sha256(response.content).hexdigest()

    async def _snapshot_ui_element(
        self,
        element,
        *,
        locator_attribute: str,
        locator_value: str,
    ) -> dict[str, object]:
        """Capture a normalized UI snapshot for generated assertions."""
        snapshot = await element.evaluate(
            """(node, context) => {
                const normalize = (value) =>
                    String(value ?? "")
                        .replace(/\\s+/g, " ")
                        .trim();
                const snapshot = {
                    locator_attribute: context.locatorAttribute,
                    locator_value: context.locatorValue,
                    tag_name: normalize(node.tagName).toLowerCase(),
                };
                const style = window.getComputedStyle(node);
                const rect = node.getBoundingClientRect();
                const hiddenByStyle =
                    style.display === "none" ||
                    style.visibility === "hidden" ||
                    style.visibility === "collapse" ||
                    rect.width === 0 ||
                    rect.height === 0;
                snapshot.visibility_state = hiddenByStyle ? "hidden" : "visible";
                const text = normalize(node.innerText || node.textContent || "");
                const stableTextTags = new Set([
                    "a",
                    "button",
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "label",
                    "p",
                    "span",
                ]);
                if (
                    text &&
                    text.length <= 200 &&
                    (stableTextTags.has(snapshot.tag_name) || node.childElementCount === 0)
                ) {
                    snapshot.text = text;
                }
                const value = "value" in node ? normalize(node.value) : "";
                if (value) {
                    snapshot.value = value;
                }
                for (const attributeName of context.attributeNames) {
                    const attributeValue = normalize(node.getAttribute(attributeName));
                    if (attributeValue) {
                        snapshot[attributeName.replace(/-/g, "_")] = attributeValue;
                    }
                }
                for (
                    const attributeName of [
                        "id",
                        "name",
                        "type",
                        "placeholder",
                        "role",
                        "aria-label",
                        "href",
                        "src",
                    ]
                ) {
                    const attributeValue = normalize(node.getAttribute(attributeName));
                    if (attributeValue) {
                        snapshot[attributeName.replace(/-/g, "_")] = attributeValue;
                    }
                }
                const backgroundImage = style.backgroundImage || "";
                const backgroundMatch = backgroundImage.match(/url\\((['"]?)(.*?)\\1\\)/);
                if (backgroundMatch && backgroundMatch[2]) {
                    snapshot.background_image_url = normalize(backgroundMatch[2]);
                }
                if (!snapshot.src) {
                    const nestedImage = node.querySelector("img");
                    const nestedImageSrc = normalize(
                        nestedImage?.currentSrc || nestedImage?.getAttribute("src") || ""
                    );
                    if (nestedImageSrc) {
                        snapshot.image_src = nestedImageSrc;
                    }
                }
                return snapshot;
            }""",
            {
                "locatorAttribute": locator_attribute,
                "locatorValue": locator_value,
                "attributeNames": list(TARGET_ATTRIBUTES),
            },
        )
        asset_url = str(
            snapshot.get("src")
            or snapshot.get("image_src")
            or snapshot.get("background_image_url")
            or ""
        ).strip()
        if asset_url:
            image_sha256 = await self._fetch_asset_sha256(asset_url)
            if image_sha256:
                snapshot["image_sha256"] = image_sha256
        return snapshot

    async def harvest_ui_elements(self, page: Page) -> set[str]:
        """Collect all currently attached stable target attributes."""
        current: set[str] = set()
        for attribute in TARGET_ATTRIBUTES:
            for element in await page.query_selector_all(f"[{attribute}]"):
                try:
                    value = await element.get_attribute(attribute)
                except Exception:
                    continue
                if value:
                    current.add(value)
                    if value not in self.ui_element_details:
                        try:
                            self.ui_element_details[value] = await self._snapshot_ui_element(
                                element,
                                locator_attribute=attribute,
                                locator_value=value,
                            )
                        except Exception:
                            continue
        self.discovered_ui_elements.update(current)
        return current

    async def _sniff_ephemeral_elements(
        self,
        page: Page,
        stop: asyncio.Event,
        interval_ms: int,
    ) -> None:
        """Harvest short-lived targets while the main scan advances the page."""
        while not stop.is_set():
            await page.wait_for_timeout(interval_ms)
            if stop.is_set():
                break
            await self.harvest_ui_elements(page)

    async def execute_progressive_multi_pass_scan(
        self,
        page: Page,
        *,
        distance: int = 350,
        step_delay_ms: int = 600,
        sniff_interval_ms: int = 100,
        max_steps: int = 100,
    ) -> None:
        """Scroll incrementally and continuously harvest dynamic UI targets."""
        if min(distance, step_delay_ms, sniff_interval_ms, max_steps) <= 0:
            raise ValueError("Progressive scan settings must be positive")

        await self.harvest_ui_elements(page)
        stop = asyncio.Event()
        sniffer = asyncio.create_task(
            self._sniff_ephemeral_elements(page, stop, sniff_interval_ms)
        )
        current_scroll = 0
        steps = 0
        try:
            total_height = int(await page.evaluate("document.body.scrollHeight"))
            while current_scroll < total_height and steps < max_steps:
                await page.evaluate(f"window.scrollBy(0, {distance})")
                current_scroll += distance
                steps += 1
                await page.wait_for_timeout(step_delay_ms)
                await self.harvest_ui_elements(page)
                total_height = int(await page.evaluate("document.body.scrollHeight"))
        finally:
            stop.set()
            await sniffer

        final_elements = await self.harvest_ui_elements(page)
        self.ui_element_presence = {
            target: "deterministic" if target in final_elements else "ephemeral"
            for target in self.discovered_ui_elements
        }

    async def scrape_page(
        self,
        target_path: str,
        *,
        auth_state_path: str | Path | None = None,
        save_state_path: str | Path | None = None,
        headless: bool = True,
        scan_distance: int = 350,
        step_delay_ms: int = 600,
        sniff_interval_ms: int = 100,
        max_scan_steps: int = 100,
        challenge_timeout_ms: int = 15_000,
    ) -> dict[str, object]:
        """Visit a route and return its discovered application manifest."""
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context_options: dict[str, object] = {
                "locale": "en-US",
                "user_agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
                ),
                "viewport": {"width": 1280, "height": 720},
                "color_scheme": "light",
                "extra_http_headers": {"Accept-Language": "en-US,en;q=0.9"},
            }
            if auth_state_path is not None:
                context_options["storage_state"] = str(auth_state_path)
            context = await browser.new_context(**context_options)
            await Stealth().apply_stealth_async(context)
            page = await context.new_page()

            async def filter_and_monitor(request: Request):
                if request.resource_type in ("fetch", "xhr") or "/api/" in request.url:
                    await self.monitor_network(request)

            page.on("request", lambda request: asyncio.create_task(filter_and_monitor(request)))

            try:
                await page.goto(
                    f"{self.base_url}/{target_path.lstrip('/')}",
                    wait_until="domcontentloaded",
                )
                challenge_cleared = await self.handle_security_challenges(
                    page,
                    timeout_ms=challenge_timeout_ms,
                )
                if challenge_cleared:
                    await self.handle_cookie_banner(page)
                    if self.scraper:
                        self.discovered_api_endpoints = await self.scraper.scrape(page)
                    await self.execute_progressive_multi_pass_scan(
                        page,
                        distance=scan_distance,
                        step_delay_ms=step_delay_ms,
                        sniff_interval_ms=sniff_interval_ms,
                        max_steps=max_scan_steps,
                    )
                if save_state_path is not None:
                    await context.storage_state(path=str(save_state_path))
            finally:
                await context.close()
                await browser.close()
        return self.application_manifest(target_path)

    async def scrape_documentation_file(self, file_name: str) -> dict[str, object]:
        """Parse a documentation snapshot from coverage_agent/plugins/documentation_sources."""
        if self.scraper is None:
            raise ValueError(f"No documentation scraper registered for {self.base_url}")
        self.discovery_mode = "documentation_file"
        source_path = self.documentation_source_path(file_name)
        content = source_path.read_text(encoding="utf-8")
        self.discovered_api_endpoints = await self.scraper.scrape_content(content)
        self.discovered_ui_elements.clear()
        self.ui_element_details = {}
        self.ui_element_presence = {}
        self.security_challenge_status = "not_detected"
        self.security_challenge_selector = None
        return self.application_manifest(self.documentation_source_page(source_path.name))

    def empty_ui_reason(self) -> str | None:
        """Explain why no UI elements were recorded, when applicable."""
        if self.discovered_ui_elements:
            return None
        if self.discovery_mode == "documentation_file":
            return "Documentation-file discovery does not scan UI elements."
        if self.security_challenge_status == "unresolved":
            return "UI scan did not run because a security challenge remained unresolved."
        return (
            "No elements with stable target attributes were found during the scan "
            f"({', '.join(TARGET_ATTRIBUTES)})."
        )

    def empty_api_reason(self) -> str | None:
        """Explain why no API endpoints were recorded, when applicable."""
        if self.discovered_api_endpoints:
            return None
        if self.discovery_mode == "documentation_file":
            return "The selected documentation scraper did not extract any API endpoints from the file."
        if self.security_challenge_status == "unresolved":
            return "API discovery did not complete because a security challenge remained unresolved."
        if self.scraper is not None:
            return (
                "No API endpoints were extracted by the selected scraper and no same-site "
                "/api/ requests were observed on this page."
            )
        return "No same-site /api/ requests were observed on this page."

    def application_manifest(self, page: str) -> dict[str, object]:
        """Build a deterministic application map."""
        normalized_page = "/" + page.lstrip("/")

        unique_endpoints = []
        for ep in self.discovered_api_endpoints:
            if ep not in unique_endpoints:
                unique_endpoints.append(ep)

        manifest = {
            "page": normalized_page,
            "base_url": self.base_url,
            "scan_status": (
                "blocked_by_security_challenge"
                if self.security_challenge_status == "unresolved"
                else "complete"
            ),
            "security_challenge": {
                "status": self.security_challenge_status,
                "selector": self.security_challenge_selector,
            },
            "discovered_ui_elements": sorted(self.discovered_ui_elements),
            "ui_element_presence": {
                target: self.ui_element_presence.get(target, "deterministic")
                for target in sorted(self.discovered_ui_elements)
            },
            "ui_element_details": {
                target: self.ui_element_details[target]
                for target in sorted(self.discovered_ui_elements)
                if target in self.ui_element_details
            },
            "discovered_api_endpoints": sorted(
                unique_endpoints,
                key=lambda x: (
                    x["path"],
                    x["method"],
                    x.get("response_code", ""),
                ),
            ),
            "empty_ui_reason": self.empty_ui_reason(),
            "empty_api_reason": self.empty_api_reason(),
        }
        return manifest

    def write_application_manifest(self, page: str, output_file: str | Path) -> None:
        """Write the current application map to JSON."""
        destination = Path(output_file)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(self.application_manifest(page), indent=2) + "\n",
            encoding="utf-8",
        )
