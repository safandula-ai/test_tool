# Test Framework Scaffold

Modular UI and API test framework built around `pytest`, async `Playwright`, `httpx`, `jsonschema`, `allure-pytest`, `python-dotenv`, and `loguru`.

The example integrations target SauceDemo for browser E2E coverage, ReqRes for paginated API contract testing, and Automation Exercise for same-system API/UI hybrid testing.

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and adjust the target URLs.
4. Install Playwright browsers with `playwright install`.

## Environment Setup

The framework reads configuration from environment variables and `.env` files.

- `ENV`: `local`, `staging`, or `prod`
- `BASE_URL`: UI target base URL
- `API_BASE_URL`: API target base URL
- `HEADLESS`: run browser headless when `true`
- `TRACE_ON_FAILURE`: enable trace capture for failed UI tests
- `REQRES_API_KEY`: required by ReqRes for live API requests
- `RUN_LIVE_TESTS`: opt in to tests that call external services
- `AUTOMATION_EXERCISE_BASE_URL`: UI and API base URL for advanced tests
- `UPDATE_VISUAL_BASELINES`: create or replace visual regression baselines

## Running Tests

Run all tests:

```bash
pytest
```

## Coverage Gap Agent

Tests can declare the UI element or API endpoint they cover with
`@covers(type=..., target=..., priority=..., template=...)`. Generate the static
map, discover a live route, and produce a gap report with:

```powershell
python -m coverage_agent analyze --tests tests --output reports/coverage_map.json
python -m coverage_agent discover --base-url https://automationexercise.com --path /login
python -m coverage_agent gaps
```

The discovery command captures `data-testid`, `data-test`, and `data-qa`
targets, filters same-site `/api/` traffic, and can reuse Playwright storage
state through `--auth-state` and `--save-state`.

Run only API tests:

```bash
pytest -m api
```

Run only UI tests:

```bash
pytest -m ui
```

Run human-readable BDD scenarios:

```bash
pytest -m bdd
```

Run deterministic API contract tests without external network access:

```bash
pytest -m "api and not integration"
```

Run live SauceDemo and ReqRes tests after setting `REQRES_API_KEY`:

```bash
RUN_LIVE_TESTS=true pytest -m "e2e or integration"
```

On PowerShell:

```powershell
$env:RUN_LIVE_TESTS = "true"
$env:REQRES_API_KEY = "your-key"
pytest -m "e2e or integration"
```

Run the Automation Exercise API-to-UI negative path:

```bash
RUN_LIVE_TESTS=true pytest -m hybrid
```

Create the initial Automation Exercise visual baseline:

```bash
RUN_LIVE_TESTS=true UPDATE_VISUAL_BASELINES=true pytest -m visual
```

Subsequent visual runs compare changed pixels against a 1% tolerance:

```bash
RUN_LIVE_TESTS=true pytest -m visual
```

## Structure

- `api_clients/`: async HTTP clients
- `pages/`: Playwright page objects
- `schemas/`: JSON Schema contracts
- `tests/api/`: API and contract tests
- `tests/ui/`: UI and E2E tests
- `tests/bdd/`: Gherkin-style readable scenarios
- `config/`: settings and environment loading
- `utils/`: logging, fake data, validation helpers

## Integration Boundary

SauceDemo does not provide a documented public API for creating orders or obtaining authenticated browser sessions. ReqRes and SauceDemo are unrelated systems, so the framework deliberately does not pretend that ReqRes data can prepare SauceDemo state. Automation Exercise exposes both a supported account API and UI, so it is used for the real hybrid flow: create a unique account through the API, verify duplicate-email handling in the UI, and delete the account during cleanup.
