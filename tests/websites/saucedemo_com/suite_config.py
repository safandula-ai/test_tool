"""Website-specific suite configuration."""

BASE_URL = "https://www.saucedemo.com"
SUITE_NAME = "saucedemo_com"
SMOKE_HEALTH_PATH = "/"
SMOKE_HEALTH_STATUS = 200
SMOKE_ROOT_PATH = "/"
SMOKE_ROOT_SELECTOR = "[data-test='login-container']"
SMOKE_REQUEST_TIMEOUT_MS = 5_000
SMOKE_RENDER_TIMEOUT_MS = 8_000
