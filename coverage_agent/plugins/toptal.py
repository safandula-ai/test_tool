from __future__ import annotations

import json
import re
from urllib.parse import urlsplit

from playwright.async_api import Page

from .base import ApiScraper


_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_REDACTED_EMAIL = "<redacted-email>"
_REDACTED_NAME = "<redacted-name>"
_REDACTED_ID = 0
_NAME_KEYS = {
    "full_name",
    "first_name",
    "last_name",
    "name",
}
_EXACT_REDACTED_KEYS = {
    "email": _REDACTED_EMAIL,
}


def sanitize_toptal_response_payload(payload: object) -> object:
    """Redact identity-bearing fields while preserving response structure."""

    def sanitize(value: object, *, key: str | None = None) -> object:
        lowered_key = (key or "").lower()
        if isinstance(value, dict):
            return {
                nested_key: sanitize(nested_value, key=str(nested_key))
                for nested_key, nested_value in value.items()
            }
        if isinstance(value, list):
            return [sanitize(item, key=key) for item in value]
        if lowered_key in _EXACT_REDACTED_KEYS:
            return _EXACT_REDACTED_KEYS[lowered_key]
        if lowered_key in _NAME_KEYS or (
            "name" in lowered_key and isinstance(value, str) and value.strip()
        ):
            return _REDACTED_NAME
        if lowered_key == "id" or lowered_key.endswith("_id"):
            return _REDACTED_ID if isinstance(value, (int, float)) else "<redacted-id>"
        if isinstance(value, str) and _EMAIL_PATTERN.match(value.strip()):
            return _REDACTED_EMAIL
        return value

    return sanitize(payload)


async def _discover_api_urls(page: Page, base_origin: str) -> list[str]:
    """Read same-origin API resource URLs observed by the page."""
    urls = await page.evaluate(
        """(baseOrigin) => {
            const entries = performance.getEntriesByType("resource");
            return entries
                .map((entry) => String(entry.name || ""))
                .filter((name) => name.startsWith(baseOrigin) && name.includes("/api/"));
        }""",
        base_origin,
    )
    unique_urls: list[str] = []
    for url in urls:
        if url not in unique_urls:
            unique_urls.append(url)
    return unique_urls


async def _fetch_endpoint_sample(page: Page, path: str) -> dict[str, str] | None:
    """Fetch one same-origin API endpoint from inside the browser context."""
    sample = await page.evaluate(
        """async (path) => {
            try {
                const response = await fetch(path, {
                    method: "GET",
                    credentials: "include",
                    headers: { Accept: "application/json" },
                });
                const contentType = response.headers.get("content-type") || "";
                const text = await response.text();
                return {
                    status: response.status,
                    content_type: contentType,
                    text,
                };
            } catch (error) {
                return {
                    error: String(error),
                };
            }
        }""",
        path,
    )
    if not isinstance(sample, dict) or sample.get("error"):
        return None
    endpoint_data: dict[str, str] = {
        "response_code": str(sample.get("status", "")),
    }
    content_type = str(sample.get("content_type", "")).lower()
    text = str(sample.get("text", "")).strip()
    if "application/json" not in content_type or not text:
        return endpoint_data
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return endpoint_data
    endpoint_data["response_payload_kind"] = "json"
    endpoint_data["response_payload"] = json.dumps(
        sanitize_toptal_response_payload(payload),
        sort_keys=True,
    )
    return endpoint_data


class ToptalScraper(ApiScraper):
    """Live API scraper for toptal.com endpoints discovered from homepage traffic."""

    async def scrape(self, page: Page) -> list[dict[str, str]]:
        base_origin = "{0.scheme}://{0.netloc}".format(urlsplit(page.url))
        discovered_api_endpoints: list[dict[str, str]] = []
        for full_url in await _discover_api_urls(page, base_origin):
            parsed = urlsplit(full_url)
            if "/api/" not in parsed.path:
                continue
            endpoint_data: dict[str, str] = {
                "method": "GET",
                "path": parsed.path,
                "full_url": full_url,
            }
            sample = await _fetch_endpoint_sample(page, parsed.path)
            if sample:
                endpoint_data.update(sample)
            if endpoint_data not in discovered_api_endpoints:
                discovered_api_endpoints.append(endpoint_data)
        return discovered_api_endpoints

    async def enrich_endpoints(
        self,
        page: Page,
        endpoints: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        enriched: list[dict[str, str]] = []
        base_origin = "{0.scheme}://{0.netloc}".format(urlsplit(page.url))
        for endpoint in endpoints:
            merged = dict(endpoint)
            path = str(endpoint.get("path", ""))
            method = str(endpoint.get("method", "")).upper()
            if path.startswith("/api/"):
                merged.setdefault("full_url", f"{base_origin}{path}")
            if method == "GET" and path.startswith("/api/"):
                sample = await _fetch_endpoint_sample(page, path)
                if sample:
                    merged.update(sample)
            enriched.append(merged)
        return enriched
