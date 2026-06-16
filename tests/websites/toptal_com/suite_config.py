"""Website-specific suite configuration."""

BASE_URL = "https://www.toptal.com"
SUITE_NAME = "toptal_com"
MOBILE_VIEWPORT = {"width": 390, "height": 844}
MOBILE_USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 "
    "Mobile/15E148 Safari/604.1"
)
SMOKE_HEALTH_PATH = "/"
SMOKE_HEALTH_STATUS = 200
SMOKE_ROOT_PATH = "/"
SMOKE_ROOT_SELECTOR = "[data-testid='nav-container']"
SMOKE_REQUEST_TIMEOUT_MS = 5_000
SMOKE_RENDER_TIMEOUT_MS = 8_000
PERF_HOME_PATH = "/"
PERF_HOME_READY_SELECTOR = "[data-testid='nav-container']"
PERF_MOBILE_PATH = "/"
PERF_MOBILE_READY_SELECTOR = "[data-testid='nav-container']"
SECURITY_SEARCH_PATH = "/"
SECURITY_SEARCH_INPUT_SELECTOR = "input[type='search'], input[name='search'], input[type='text']"
SECURITY_SEARCH_SUBMIT_SELECTOR = "button[type='submit'], input[type='submit']"
SECURITY_CONSENT_ROOT_SELECTOR = ".fc-consent-root"
SECURITY_CONSENT_ACCEPT_SELECTOR = ".fc-cta-consent, button:has-text('Consent'), button:has-text('Accept')"
SECURITY_CONSENT_OVERLAY_SELECTOR = ".fc-dialog-overlay"
