param(
    [string]$Results = "allure-results",
    [string]$Output = "allure-report",
    [string]$Name = ""
)

$python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    $python = "python"
}

$arguments = @(
    (Join-Path $PSScriptRoot "generate_allure_report.py"),
    "--results", $Results,
    "--output", $Output
)
if ($Name) {
    $arguments += @("--name", $Name)
}

& $python @arguments
exit $LASTEXITCODE
