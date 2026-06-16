"""Allure CLI discovery, timestamped report archives, and history retention."""

from __future__ import annotations

import secrets
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


_ADJECTIVES = ("bright", "calm", "clear", "quick", "steady", "vivid")
_NOUNS = ("bridge", "cloud", "harbor", "meadow", "river", "summit")


@dataclass(frozen=True)
class AllureGenerationResult:
    """Outcome of an Allure HTML generation attempt."""

    status: str
    message: str
    returncode: int = 0
    report_dir: Path | None = None

    @property
    def succeeded(self) -> bool:
        return self.status == "generated"


def generate_report_name(now: datetime | None = None) -> str:
    """Return a sortable timestamp plus a readable random suffix."""
    timestamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    return f"{timestamp}-{secrets.choice(_ADJECTIVES)}-{secrets.choice(_NOUNS)}"


def _unique_report_dir(archive: Path, report_name: str | None) -> Path:
    base_name = report_name or generate_report_name()
    candidate = archive / base_name
    counter = 2
    while candidate.exists():
        candidate = archive / f"{base_name}-{counter}"
        counter += 1
    return candidate


def _run_allure(command: list[str]) -> subprocess.CompletedProcess[str]:
    logger.info(f"Running Allure command: {' '.join(command)}")
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
    )


def generate_allure_report(
    results_dir: str | Path = "allure-results",
    report_dir: str | Path = "allure-report",
    *,
    allure_command: str = "allure",
    report_name: str | None = None,
) -> AllureGenerationResult:
    """Generate an archived single-file report and preserve trend history."""
    results = Path(results_dir)
    archive = Path(report_dir)
    executable = shutil.which(allure_command)
    if executable is None:
        return AllureGenerationResult(
            "cli_missing",
            "Allure CLI was not found on PATH. Please install it from https://allurereport.org/",
        )
    if not results.exists() or not any(results.iterdir()):
        return AllureGenerationResult(
            "no_results",
            f"No Allure results found in {results}.",
        )

    archive.mkdir(parents=True, exist_ok=True)
    history_store = archive / ".history"
    results_history = results / "history"
    if history_store.is_dir():
        shutil.copytree(history_store, results_history, dirs_exist_ok=True)

    output = _unique_report_dir(archive, report_name)
    build_dir = archive / ".history-build"
    history_command = [
        executable,
        "generate",
        str(results),
        "--clean",
        "-o",
        str(build_dir),
    ]
    completed = _run_allure(history_command)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        return AllureGenerationResult(
            "generation_failed",
            detail or "Allure CLI failed while updating report history.",
            completed.returncode,
        )

    generated_history = build_dir / "history"
    if generated_history.is_dir():
        shutil.copytree(generated_history, history_store, dirs_exist_ok=True)
    shutil.rmtree(build_dir, ignore_errors=True)

    report_command = [
        executable,
        "generate",
        str(results),
        "--clean",
        "--single-file",
        "-o",
        str(output),
    ]
    completed = _run_allure(report_command)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        return AllureGenerationResult(
            "generation_failed",
            detail or "Allure CLI failed without diagnostic output.",
            completed.returncode,
        )

    latest = archive / "latest.txt"
    latest.write_text(str(output.resolve()), encoding="utf-8")
    return AllureGenerationResult(
        "generated",
        f"Allure report generated in {output}; history stored in {history_store}.",
        report_dir=output,
    )
