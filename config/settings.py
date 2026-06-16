from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class ApiDocSettings:
    """Settings for parsing API documentation."""

    url_keywords: list[str]
    method_keywords: list[str]
    request_parameter_keywords: list[str]
    response_code_keywords: list[str]
    response_payload_keywords: list[str]


@dataclass(frozen=True)
class Settings:
    """Resolved runtime configuration for the test framework."""

    env: str
    base_url: str
    api_base_url: str
    reqres_api_key: str | None
    sauce_username: str
    sauce_password: str
    update_visual_baselines: bool
    headless: bool
    slow_mo: int
    trace_on_failure: bool
    screenshot_on_failure: bool
    video_on_failure: bool
    log_level: str
    http_timeout: float
    artifact_dir: Path
    screenshot_dir: Path
    video_dir: Path
    api_doc_settings: ApiDocSettings


def _bool(name: str, default: str = "false") -> bool:
    """Parse a truthy environment variable flag."""
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once and create the framework artifact directories."""
    artifact_dir = ROOT / "reports"
    screenshot_dir = artifact_dir / "screenshots"
    video_dir = artifact_dir / "videos"
    for path in (artifact_dir, screenshot_dir, video_dir, ROOT / "logs"):
        path.mkdir(parents=True, exist_ok=True)

    return Settings(
        env=os.getenv("ENV", "local"),
        base_url=os.getenv("BASE_URL", "https://www.saucedemo.com"),
        api_base_url=os.getenv("API_BASE_URL", "http://localhost:3000"),
        reqres_api_key=os.getenv("REQRES_API_KEY") or None,
        sauce_username=os.getenv("SAUCE_USERNAME", "standard_user"),
        sauce_password=os.getenv("SAUCE_PASSWORD", "secret_sauce"),
        update_visual_baselines=_bool("UPDATE_VISUAL_BASELINES", "false"),
        headless=_bool("HEADLESS", "true"),
        slow_mo=int(os.getenv("SLOW_MO", "0")),
        trace_on_failure=_bool("TRACE_ON_FAILURE", "true"),
        screenshot_on_failure=_bool("SCREENSHOT_ON_FAILURE", "true"),
        video_on_failure=_bool("VIDEO_ON_FAILURE", "true"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        http_timeout=float(os.getenv("HTTP_TIMEOUT", "10")),
        artifact_dir=artifact_dir,
        screenshot_dir=screenshot_dir,
        video_dir=video_dir,
        api_doc_settings=ApiDocSettings(
            url_keywords=os.getenv("API_DOC_URL_KEYWORDS", "API URL:,Request URL:").split(","),
            method_keywords=os.getenv("API_DOC_METHOD_KEYWORDS", "Request Method:").split(","),
            request_parameter_keywords=os.getenv(
                "API_DOC_REQUEST_PARAMETER_KEYWORDS",
                "Request Parameters:,Request Parameter:",
            ).split(","),
            response_code_keywords=os.getenv(
                "API_DOC_RESPONSE_CODE_KEYWORDS",
                "Response Code:",
            ).split(","),
            response_payload_keywords=os.getenv(
                "API_DOC_RESPONSE_PAYLOAD_KEYWORDS",
                "Response JSON:,Response Message:,Response Payload:",
            ).split(","),
        ),
    )
