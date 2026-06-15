# Test Framework Scaffold

Modular UI and API test framework built around `pytest`, async `Playwright`, `httpx`, `jsonschema`, `allure-pytest`, `python-dotenv`, and `loguru`.

The example integrations target SauceDemo for browser E2E coverage, ReqRes for paginated API contract testing, and Automation Exercise for same-system API/UI hybrid testing.

## Quick Start

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
playwright install chromium
```

### Linux

Debian or Ubuntu prerequisites:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip
```

Project setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
playwright install --with-deps chromium
```

Adjust target URLs and credentials in `.env` after copying the example file.

## Environment Setup

The framework reads configuration from environment variables and `.env` files.

- `ENV`: `local`, `staging`, or `prod`
- `BASE_URL`: UI target base URL
- `PERFORMANCE_MAX_RESPONSE_MS`: generic performance threshold, default `5000`
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

## Allure Reporting

`allure-pytest` is installed through `requirements.txt` and collects test
results. The separate Allure CLI is required to render or open the HTML report.

The Python virtual environment does not provide the `allure` executable. Allure
Report 2 runs on Java, so install a Java runtime first. On Windows:

```powershell
winget install --id EclipseAdoptium.Temurin.17.JRE --exact
java -version
```

### Install Allure On Windows

The official Allure project recommends Scoop for Windows. Install Scoop for
the current user, then install Allure:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
scoop install allure
```

Close and reopen PowerShell, then verify the installation:

```powershell
allure --version
Get-Command allure
```

If Scoop is not permitted, use the manual installation instead:

1. Download the latest `allure-*.zip` asset from the official releases page:

   https://github.com/allure-framework/allure2/releases

2. Extract it, for example to `C:\Tools\allure`.
3. Add its `bin` directory to the user `PATH`:

```powershell
$allureBin = "C:\Tools\allure\bin"
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";" + $allureBin,
  "User"
)
```

Close and reopen PowerShell after changing `PATH`, then verify:

```powershell
java -version
allure --version
```

Do not prefix Allure commands with `python`. `allure` is a standalone command,
not a Python module. If `allure --version` still fails, confirm that
`C:\Tools\allure\bin\allure.bat` exists and that the new terminal sees the
updated user `PATH`.

If Allure reports that `JAVA_HOME` is missing or invalid, locate the installed
Temurin directory and set it without adding quotes to the stored value:

```powershell
$javaHome = Get-ChildItem "C:\Program Files\Eclipse Adoptium" -Directory |
  Where-Object { Test-Path (Join-Path $_.FullName "bin\java.exe") } |
  Select-Object -First 1 -ExpandProperty FullName

[Environment]::SetEnvironmentVariable("JAVA_HOME", $javaHome, "User")
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";" +
    (Join-Path $javaHome "bin"),
  "User"
)
```

Open a new PowerShell window and verify:

```powershell
echo $env:JAVA_HOME
java -version
allure --version
```

### Install Allure On Linux

On Debian or Ubuntu, install Java and the download utilities first:

```bash
sudo apt-get update
sudo apt-get install -y openjdk-17-jre-headless curl jq
java -version
```

Download the latest official Allure release, extract it under `/opt`, and add
an executable link to `/usr/local/bin`:

```bash
ALLURE_VERSION=$(curl -fsSL \
  https://api.github.com/repos/allure-framework/allure2/releases/latest |
  jq -r .tag_name)
curl -fsSL -o /tmp/allure.tgz \
  "https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz"
sudo mkdir -p /opt/allure
sudo tar -xzf /tmp/allure.tgz -C /opt/allure --strip-components=1
sudo ln -sf /opt/allure/bin/allure /usr/local/bin/allure
allure --version
```

If Allure cannot find Java, persist `JAVA_HOME` in your shell configuration:

```bash
JAVA_HOME=$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")
echo "export JAVA_HOME=$JAVA_HOME" >> ~/.bashrc
echo 'export PATH="$JAVA_HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
java -version
allure --version
```

Every pytest run replaces the temporary `allure-results/` directory and creates
a new archived report under `allure-report/` when the standalone Allure CLI is
on `PATH`. Report directories use a sortable timestamp and readable random
suffix, for example `20260615-143045-clear-harbor`, so previous reports are not
overwritten:

```bash
pytest
```

If the CLI is unavailable, pytest preserves its normal exit code and prints an
`ALLURE WARNING`. Set `ALLURE_REPORT_REQUIRED=true` in CI to fail an otherwise
successful run when HTML generation is unavailable or fails. Disable only the
HTML generation step with `pytest --no-allure-report`; raw results are still
collected.

Require successful HTML generation in CI:

Windows PowerShell:

```powershell
$env:ALLURE_REPORT_REQUIRED = "true"
pytest
```

Linux:

```bash
ALLURE_REPORT_REQUIRED=true pytest
```

Generate a temporary report and open it in a browser:

```bash
allure serve allure-results
```

Generate a timestamped persistent single-file report in `allure-report/`. Each
run contains an `index.html` that can be opened directly from the filesystem.
`allure-report/latest.txt` contains the absolute path of the newest run.
`allure-report/.history/` stores Allure trend data and is copied into the next
run automatically.

Windows PowerShell:

```powershell
./scripts/generate_allure_report.ps1
$latest = Get-Content ./allure-report/latest.txt
Start-Process (Join-Path $latest "index.html")
```

Linux:

```bash
python scripts/generate_allure_report.py
LATEST=$(cat ./allure-report/latest.txt)
xdg-open "$LATEST/index.html"
```

After installation, a normal test run performs the full workflow:

```bash
pytest
# Open the run referenced by allure-report/latest.txt.
```

Provide a custom run name when needed. If that directory already exists, the
generator appends `-2`, `-3`, and so on instead of replacing it:

Windows PowerShell:

```powershell
./scripts/generate_allure_report.ps1 -Name "release-2026-06"
```

Linux:

```bash
python scripts/generate_allure_report.py --name "release-2026-06"
```

Older multi-file Allure reports must be opened through `allure open
allure-report`; opening their `index.html` through `file://` causes `Failed to
fetch` errors because browsers block the report's JSON requests. This project
uses Allure's `--single-file` mode to avoid that restriction.

Official references:

- https://github.com/allure-framework/allure2
- https://github.com/allure-framework/allure2/releases

## Coverage Gap Agent

Tests declare the UI element or API endpoint they cover with `@covers`:

```python
@covers(
    type="ui",
    target="login-email",
    priority="high",
    presence="deterministic",
    template="InputValidationTemplate",
    page="/login",
    feature="feature:authentication",
)
```

### End-to-End Workflow

1. Generate the static coverage map from test decorators:

```bash
python -m coverage_agent analyze --tests tests --output reports/coverage_map.json
```

2. Discover the live page surface. The scraper progressively scrolls through
   the route, continuously captures `data-testid`, `data-test`, and `data-qa`
   attributes, records same-site `/api/` traffic, and applies
   `playwright-stealth` before creating browser pages:

```bash
python -m coverage_agent discover --base-url https://automationexercise.com --path /login
```

When `--base-url` is omitted, discovery uses `BASE_URL` from `.env`. Discovery
creates or reuses `tests/websites/<hostname>/` with `suite_config.py` and the
standard `api/`, `ui/`, `smoke/`, `performance/`, and `generated/` packages.

Use `--auth-state` to load a Playwright storage-state file and `--save-state`
to save the resulting session. Tune dynamic-page scanning with
`--scan-distance`, `--step-delay-ms`, `--sniff-interval-ms`, and
`--max-scan-steps`. Security interstitials are detected before scanning and
wait up to 15 seconds by default; override that bound with
`--challenge-timeout-ms`.

The application map records challenge handling as `not_detected`, `cleared`,
or `unresolved`. An unresolved challenge prevents surface harvesting, writes
`scan_status: blocked_by_security_challenge`, and makes `discover` return exit
code `2` instead of publishing a misleading empty scan.

Targets still attached at the final scan are classified as `deterministic`.
Targets harvested during the scan but absent from the final DOM are classified
as `ephemeral`, which covers temporary banners, recycled virtual-DOM rows, and
animation-driven widgets. The application map stores this in
`ui_element_presence` while retaining the existing target lists.

3. Compare discovered targets with decorated tests:

```bash
python -m coverage_agent gaps
```

The report is written to `reports/gap_report.json`. A missing entry resembles:

```text
ERROR UI login-email (deterministic) -> InputValidationTemplate
WARNING UI temporary-toast (ephemeral) -> ComponentVisibilityTemplate
```

Deterministic UI gaps and all API gaps are added to `errors`, and the command
returns exit code `1`. Ephemeral UI gaps are added to `warnings`, receive the
same blueprint recommendations, and do not fail the build.

4. Scaffold executable checks for supported UI gaps:

```bash
python -m coverage_agent scaffold-gaps
```

The gap report's `base_url` selects the website suite automatically. For
example, Automation Exercise output is written to
`tests/websites/automationexercise_com/generated/test_generated_coverage_gaps.py`.
Use `--output` only when a custom location is required. Supported UI templates
generate executable Playwright assertions and literal `@covers` decorators.
API and domain-specific gaps generate `todo_generated_*` functions without
active decorators, so unfinished placeholders cannot falsely close a gap.

5. Review and execute the generated tests against the live target:

Windows PowerShell:

```powershell
$env:RUN_LIVE_TESTS = "true"
pytest tests/websites/automationexercise_com/generated
```

Linux:

```bash
RUN_LIVE_TESTS=true pytest tests/websites/automationexercise_com/generated
```

6. Regenerate metadata and confirm the result:

```bash
python -m coverage_agent analyze
python -m coverage_agent gaps
```

Do not treat generated assertions as permanent coverage until they have passed
against the intended environment and their behavior matches the product
contract.

### Current Login Map

The current `reports/application_map.json` describes `/login` with six UI
targets and no observed API requests:

```json
{
  "page": "/login",
  "discovered_ui_elements": [
    "login-button",
    "login-email",
    "login-password",
    "signup-button",
    "signup-email",
    "signup-name"
  ],
  "discovered_api_endpoints": []
}
```

After covering `login-email` and `login-password` with
`test_login_fields_enforce_input_constraints`, the current result is:

```text
UI: 100.0% (6/6)
API: 100.0% (0/0)
```

### Templates and Selection

Page manifests in `config/test_manifests.json` bind discovered targets to
reusable templates and `feature:*` groups. Assemble and select suites with:

```bash
python -m coverage_agent assemble --application reports/application_map.json
python -m coverage_agent indexes
python -m coverage_agent select --template FormValidationTemplate
python -m coverage_agent select --page /login --feature feature:authentication
```

Unbound targets receive complementary template recommendations. For example,
`subscription-form` maps to form validation and submission templates, while
`discount-code` maps to input validation and coupon API templates.

### Website Suites

Provider tests are grouped by hostname:

```text
tests/websites/
  automationexercise_com/
  reqres_in/
  saucedemo_com/
  toptal_com/
```

Every website package has `suite_config.py` and consistent `api/`, `ui/`,
`smoke/`, `performance/`, and `generated/` directories. Generic smoke and
performance tests use `BASE_URL` by default. Override it directly from the
terminal:

Windows PowerShell:

```powershell
pytest tests/websites/reqres_in/smoke --target-url https://reqres.in
pytest tests/websites/automationexercise_com/performance `
  --target-url https://automationexercise.com
```

Linux:

```bash
pytest tests/websites/reqres_in/smoke --target-url https://reqres.in
pytest tests/websites/automationexercise_com/performance \
  --target-url https://automationexercise.com
```

Passing `--target-url` enables these explicit live checks even when
`RUN_LIVE_TESTS=false`.

Each smoke suite contains two critical checks:

- `test_backend_gateway_health` uses Playwright's request context and does not
  launch a browser. It requires the configured status within 5 seconds.
- `test_homepage_shell_renders` requires navigation within 8 seconds and the
  configured application-shell selector to become visible within 5 seconds.

Successful smoke checks print a `SMOKE DIAGNOSTICS` JSON block even with
pytest output capture enabled. It includes the request method, final URL, HTTP
status, elapsed milliseconds, response headers, and selector/status
expectations. The same JSON is attached to the Allure result. Credential-bearing
headers such as `authorization`, `cookie`, API keys, and tokens are redacted.

All repository tests also print a final `TEST DIAGNOSTICS` JSON block. It is
written both to the pytest terminal stream and to the individual test's
captured teardown output, so IDE test runners such as IntelliJ/PyCharm show it
when that test is selected. It
contains the test node ID, outcome, duration, markers, and any captured HTTP or
browser events. Shared HTTPX clients record request URLs, sanitized request and
response headers, statuses, and elapsed time. Shared Playwright pages record
document/XHR/fetch responses, failed requests, console warnings/errors, and
page exceptions. Tests without network or browser activity still report their
duration, markers, and result. The same payload is attached to Allure.

Configure these safeguards in each website's `suite_config.py` with
`SMOKE_HEALTH_PATH`, `SMOKE_HEALTH_STATUS`, `SMOKE_ROOT_PATH`, and
`SMOKE_ROOT_SELECTOR`. The defaults probe `/`; replace `SMOKE_HEALTH_PATH`
with a dedicated endpoint such as `/api/v1/health` when the application
provides one.

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

```text
api_clients/                 Async API clients and endpoint wrappers
config/
  settings.py                Environment and runtime settings
  test_manifests.json        Page, feature, target, and template bindings
coverage_agent/
  analyzer.py                Static @covers extraction and reverse indexes
  blueprints.py              Reusable test templates and recommendations
  decorators.py              Runtime @covers metadata
  discovery.py               Playwright UI/API discovery and challenge handling
  gap_analysis.py            Coverage correlation, errors, and warnings
  gap_scaffolder.py          Executable generated gap tests
  manifests.py               Test-manifest loading and validation
  suite_layout.py            Website package and smoke/performance scaffolding
  template_engine.py         Dynamic suite assembly and test selection
  __main__.py                coverage_agent command-line entry point
data/                        Test data and visual baselines
pages/                       Async and synchronous Playwright page objects
schemas/                     JSON Schema API contracts
scripts/
  generate_allure_report.py  Cross-platform Allure HTML generator
  generate_allure_report.ps1 PowerShell wrapper for report generation
tests/
  api/                       Provider-neutral mocked API contracts
  features/
    authentication/          Feature configuration, UI, and BDD login tests
  unit/                      Deterministic framework and agent tests
  websites/
    automationexercise_com/  API, UI, smoke, performance, generated tests
    reqres_in/                API, smoke, performance, generated tests
    saucedemo_com/            UI, smoke, performance, generated tests
    toptal_com/               Smoke, performance, and generated tests
utils/                       Allure, logging, mocks, schema, and visual helpers
```

Generated runtime output:

- `allure-results/`: temporary raw Allure files, replaced on each pytest run
- `allure-report/<timestamp>-<random-name>/`: immutable single-file report runs
- `allure-report/.history/`: trend history used by subsequent report runs
- `allure-report/latest.txt`: absolute path of the newest generated report
- `reports/`: coverage maps, gap reports, traces, screenshots, and videos
- `logs/`: framework execution logs

Root configuration:

- `conftest.py`: shared fixtures, URL overrides, artifacts, and Allure generation
- `pytest.ini`: test discovery, markers, asyncio, and Allure result collection
- `.env` / `.env.example`: local runtime configuration and documented defaults

## Integration Boundary

SauceDemo does not provide a documented public API for creating orders or obtaining authenticated browser sessions. ReqRes and SauceDemo are unrelated systems, so the framework deliberately does not pretend that ReqRes data can prepare SauceDemo state. Automation Exercise exposes both a supported account API and UI, so it is used for the real hybrid flow: create a unique account through the API, verify duplicate-email handling in the UI, and delete the account during cleanup.
