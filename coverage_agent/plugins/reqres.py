from __future__ import annotations

import html
import json
import re
from urllib.parse import parse_qsl, urlsplit

from playwright.async_api import Page

from .base import ApiScraper


_REQRES_ENDPOINT_HEADER_PATTERN = re.compile(
    r'<div class="flex items-center gap-0 rounded-lg border [^"]* overflow-hidden">\s*'
    r'<div[^>]*>(?P<method>GET|POST|PUT|DELETE)</div>\s*'
    r'<div[^>]*title="(?P<url>https?://reqres\.in/api/[^"]+)"[^>]*>',
    re.IGNORECASE,
)
_REQRES_API_KEY_HEADER_PATTERN = re.compile(
    r"(x-api-key:\s*)([^\r\n']+)",
    re.IGNORECASE,
)
_REQRES_STATUS_PATTERN = re.compile(r">(\d{3})\s+[A-Z]+<")


def _clean_code_block(fragment: str) -> str:
    """Strip syntax-highlighting markup and decode a documentation code block."""
    normalized = re.sub(r"</span>\s*<span[^>]*class=\"line\"[^>]*>", "\n", fragment)
    normalized = re.sub(r"<br\s*/?>", "\n", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"<[^>]+>", "", normalized)
    normalized = html.unescape(normalized)
    lines = [line.rstrip() for line in normalized.splitlines()]
    return "\n".join(lines).strip()


def _request_body_from_segment(segment: str) -> str | None:
    """Extract a JSON request body example from one endpoint card segment."""
    match = re.search(
        r"Request body.*?<pre[^>]*><code>(?P<body>.*?)</code></pre>",
        segment,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None
    cleaned = _clean_code_block(match.group("body"))
    return cleaned or None


def _curl_from_segment(segment: str) -> str | None:
    """Extract the curl example and replace the live API key with an env placeholder."""
    for match in re.finditer(r"<pre[^>]*><code>(?P<code>.*?)</code></pre>", segment, re.DOTALL):
        cleaned = _clean_code_block(match.group("code"))
        if cleaned.startswith("curl "):
            return _REQRES_API_KEY_HEADER_PATTERN.sub(r"\1${REQRES_API_KEY}", cleaned)
    return None


def _response_code_from_segment(segment: str) -> str | None:
    """Extract the documented HTTP status code from one endpoint segment."""
    match = _REQRES_STATUS_PATTERN.search(segment)
    if not match:
        return None
    return match.group(1)


def _response_payload_from_segment(segment: str) -> tuple[str | None, str | None]:
    """Extract the documented response body and classify its payload kind."""
    status_match = _REQRES_STATUS_PATTERN.search(segment)
    if not status_match:
        return None, None

    response_fragment = segment[status_match.end():]
    if "No response body" in response_fragment:
        return None, "none"

    code_match = re.search(
        r"<pre[^>]*><code>(?P<body>.*?)</code></pre>",
        response_fragment,
        re.IGNORECASE | re.DOTALL,
    )
    if not code_match:
        return None, None

    cleaned = _clean_code_block(code_match.group("body"))
    return (cleaned or None), ("json" if cleaned else None)


def _request_parameters(url: str, request_body: str | None) -> str | None:
    """Infer request parameter names from query params and top-level JSON keys."""
    parameters: list[str] = []
    parsed = urlsplit(url)
    for key, _ in parse_qsl(parsed.query, keep_blank_values=True):
        if key not in parameters:
            parameters.append(key)
    if request_body:
        try:
            payload = json.loads(request_body)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict):
            for key in payload:
                if key not in parameters:
                    parameters.append(key)
    return ", ".join(parameters) if parameters else None


def parse_reqres_markup(markup: str) -> list[dict[str, str]]:
    """Parse ReqRes endpoint cards from a captured HTML document."""
    matches = list(_REQRES_ENDPOINT_HEADER_PATTERN.finditer(markup))
    endpoints: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        segment_start = match.start()
        segment_end = matches[index + 1].start() if index + 1 < len(matches) else len(markup)
        segment = markup[segment_start:segment_end]

        method = match.group("method").upper()
        url = html.unescape(match.group("url"))
        parsed = urlsplit(url)
        description_match = re.search(
            r'<p class="text-\[11px\][^"]*">(?P<description>[^<]+)</p>',
            segment,
        )
        description = (
            html.unescape(description_match.group("description")).strip()
            if description_match
            else ""
        )
        request_body = _request_body_from_segment(segment)
        curl = _curl_from_segment(segment)
        response_code = _response_code_from_segment(segment) or "200"
        response_payload, response_payload_kind = _response_payload_from_segment(segment)

        endpoint: dict[str, str] = {
            "method": method,
            "path": parsed.path,
            "full_url": url,
            "response_code": response_code,
        }
        if description:
            endpoint["name"] = description
        request_parameters = _request_parameters(url, request_body)
        if request_parameters:
            endpoint["request_parameters"] = request_parameters
        if request_body:
            endpoint["request_body"] = request_body
        if curl:
            endpoint["curl"] = curl
        if response_payload is not None:
            endpoint["response_payload"] = response_payload
        if response_payload_kind is not None:
            endpoint["response_payload_kind"] = response_payload_kind
        if endpoint not in endpoints:
            endpoints.append(endpoint)
    return endpoints


class ReqResScraper(ApiScraper):
    """API documentation scraper for reqres.in."""

    async def scrape(self, page: Page) -> list[dict[str, str]]:
        markup = await page.content()
        return await self.scrape_content(markup)

    async def scrape_content(self, content: str) -> list[dict[str, str]]:
        return parse_reqres_markup(content)
