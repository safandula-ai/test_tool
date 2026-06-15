from __future__ import annotations

import re
from urllib.parse import urlsplit
from playwright.async_api import Page
from .base import ApiScraper
from config.settings import get_settings


class AutomationExerciseScraper(ApiScraper):
    """API documentation scraper for automationexercise.com."""

    async def scrape(self, page: Page) -> list[dict[str, str]]:
        """Scrape the page for API endpoints."""
        settings = get_settings()
        discovered_api_endpoints = []

        api_blocks = await page.evaluate('''() => {
            const panels = document.querySelectorAll('.panel');
            if (panels.length > 0) {
                return Array.from(panels).map(p => {
                    const text = p.textContent || p.innerText;
                    return text.replace(/\\s{2,}/g, '\\n').trim();
                });
            }
            const bodyText = document.body.textContent || "";
            return [bodyText.replace(/\\s{2,}/g, '\\n').trim()];
        }''')

        if not api_blocks:
            return []

        if len(api_blocks) == 1:
            api_blocks = [
                block.strip()
                for block in re.split(r"(?=API\s+\d+\s*:)", api_blocks[0])
                if block.strip()
            ]

        for block in api_blocks:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue

            url_keyword_pattern = "|".join(re.escape(k) for k in settings.api_doc_settings.url_keywords)
            method_keyword_pattern = "|".join(re.escape(k) for k in settings.api_doc_settings.method_keywords)

            url_match = re.search(fr'(?:{url_keyword_pattern})\s*(?P<url>https?://[^\s]+|/[^\s]+)', block)
            method_match = re.search(fr'(?:{method_keyword_pattern})\s*(?P<method>GET|POST|PUT|DELETE)', block, re.IGNORECASE)

            if url_match and method_match:
                url = url_match.group("url")
                method = method_match.group("method").upper()

                parsed = urlsplit(url)
                if "/api/" in parsed.path:
                    endpoint_data = {"method": method, "path": parsed.path}
                    title_line = re.sub(r"^(?:API\s*)?\d+\s*:\s*", "", lines[0], flags=re.IGNORECASE)
                    if title_line:
                        endpoint_data["name"] = title_line

                    parameter_keyword_pattern = "|".join(
                        re.escape(k) for k in settings.api_doc_settings.request_parameter_keywords
                    )
                    parameter_match = re.search(
                        fr'(?:{parameter_keyword_pattern})\s*(?P<parameters>[^\n]+)',
                        block,
                    )
                    if parameter_match:
                        endpoint_data["request_parameters"] = parameter_match.group(
                            "parameters"
                        ).strip()

                    code_keyword_pattern = "|".join(re.escape(k) for k in settings.api_doc_settings.response_code_keywords)
                    code_match = re.search(fr'(?:{code_keyword_pattern})\s*(?P<code>\d+)', block)
                    if code_match:
                        endpoint_data["response_code"] = code_match.group("code")

                    payload_keyword_pattern = "|".join(
                        re.escape(k) for k in settings.api_doc_settings.response_payload_keywords
                    )
                    payload_match = re.search(
                        fr'(?P<label>{payload_keyword_pattern})\s*(?P<payload>[^\n]+)',
                        block,
                    )
                    if payload_match:
                        endpoint_data["response_payload"] = payload_match.group("payload").strip()
                        label = payload_match.group("label").strip().lower()
                        endpoint_data["response_payload_kind"] = (
                            "json" if "json" in label else "message"
                        )

                    if endpoint_data not in discovered_api_endpoints:
                        discovered_api_endpoints.append(endpoint_data)
        
        return discovered_api_endpoints
