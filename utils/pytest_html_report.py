"""Timestamped pytest-html report path management."""

from __future__ import annotations

import os
import secrets
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from config.settings import ROOT


_ADJECTIVES = ("bright", "calm", "clear", "quick", "steady", "vivid")
_NOUNS = ("bridge", "cloud", "harbor", "meadow", "river", "summit")


@dataclass(frozen=True)
class PytestHtmlReportResult:
    """Outcome of pytest-html report path configuration."""

    status: str
    message: str
    report_path: Path | None = None

    @property
    def succeeded(self) -> bool:
        return self.status == "configured"


def generate_report_name(now: datetime | None = None) -> str:
    """Return a sortable timestamp plus a readable random suffix."""
    timestamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    return f"{timestamp}-{secrets.choice(_ADJECTIVES)}-{secrets.choice(_NOUNS)}"


def _unique_report_path(archive: Path, report_name: str | None) -> Path:
    base_name = report_name or generate_report_name()
    candidate = archive / f"{base_name}.html"
    counter = 2
    while candidate.exists():
        candidate = archive / f"{base_name}-{counter}.html"
        counter += 1
    return candidate


def prepare_pytest_html_report(
    report_dir: str | Path = "reports/pytest-html",
    *,
    report_name: str | None = None,
) -> PytestHtmlReportResult:
    """Prepare a unique self-contained pytest-html report path."""
    archive = Path(report_dir)
    if not archive.is_absolute():
        archive = ROOT / archive
    archive.mkdir(parents=True, exist_ok=True)
    output = _unique_report_path(archive, report_name)
    latest = archive / "latest.txt"
    latest.write_text(str(output.resolve()), encoding="utf-8")
    return PytestHtmlReportResult(
        "configured",
        f"pytest-html report will be written to {output}.",
        report_path=output,
    )


def artifact_file_name(
    nodeid: str,
    *,
    extension: str,
    now: datetime | None = None,
) -> str:
    """Build a timestamped, filesystem-safe artifact file name from a pytest node id."""
    timestamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", nodeid).strip("_").lower()
    return f"{timestamp}-{normalized}.{extension.lstrip('.')}"


def relative_report_link(report_path: str | Path, artifact_path: str | Path) -> str:
    """Return a relative link from the HTML report file to an artifact on disk."""
    return os.path.relpath(
        Path(artifact_path).resolve(),
        start=Path(report_path).resolve().parent,
    ).replace("\\", "/")
