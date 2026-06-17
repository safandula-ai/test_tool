from __future__ import annotations

from datetime import datetime

from utils.pytest_html_report import (
    artifact_file_name,
    generate_report_name,
    prepare_pytest_html_report,
    relative_report_link,
)


def test_report_name_contains_timestamp_and_readable_random_suffix(monkeypatch):
    choices = iter(("clear", "harbor"))
    monkeypatch.setattr("utils.pytest_html_report.secrets.choice", lambda values: next(choices))

    name = generate_report_name(datetime(2026, 6, 15, 14, 30, 45))

    assert name == "20260615-143045-clear-harbor"


def test_prepare_pytest_html_report_creates_latest_pointer(tmp_path):
    archive = tmp_path / "reports"

    result = prepare_pytest_html_report(archive, report_name="named-run")

    assert result.succeeded
    assert result.report_path == archive / "named-run.html"
    assert result.report_path.parent == archive
    assert not result.report_path.exists()
    assert (archive / "latest.txt").read_text(encoding="utf-8") == str(result.report_path.resolve())


def test_existing_report_name_gets_numeric_suffix(tmp_path):
    archive = tmp_path / "reports"
    archive.mkdir()
    (archive / "named-run.html").write_text("existing", encoding="utf-8")

    result = prepare_pytest_html_report(archive, report_name="named-run")

    assert result.report_path == archive / "named-run-2.html"


def test_artifact_file_name_includes_timestamp_and_sanitized_test_name():
    name = artifact_file_name(
        "tests/websites/toptal_com/generated/test_generated_coverage_gaps_api.py::test_case",
        extension="webm",
        now=datetime(2026, 6, 17, 17, 45, 12),
    )

    assert name == (
        "20260617-174512-"
        "tests_websites_toptal_com_generated_test_generated_coverage_gaps_api_py_test_case.webm"
    )


def test_relative_report_link_points_from_html_archive_to_artifact(tmp_path):
    report_path = tmp_path / "reports" / "pytest-html" / "run.html"
    artifact_path = tmp_path / "reports" / "videos" / "artifact.webm"

    link = relative_report_link(report_path, artifact_path)

    assert link == "../videos/artifact.webm"
