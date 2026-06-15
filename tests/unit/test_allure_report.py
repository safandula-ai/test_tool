from __future__ import annotations

from datetime import datetime
from pathlib import Path
from subprocess import CompletedProcess

from utils.allure_report import generate_allure_report, generate_report_name


def test_report_name_contains_timestamp_and_readable_random_suffix(monkeypatch):
    choices = iter(("clear", "harbor"))
    monkeypatch.setattr("utils.allure_report.secrets.choice", lambda values: next(choices))

    name = generate_report_name(datetime(2026, 6, 15, 14, 30, 45))

    assert name == "20260615-143045-clear-harbor"


def test_allure_generation_reports_missing_cli(tmp_path, monkeypatch):
    results = tmp_path / "results"
    results.mkdir()
    (results / "result.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr("utils.allure_report.shutil.which", lambda command: None)

    result = generate_allure_report(results, tmp_path / "reports")

    assert result.status == "cli_missing"
    assert not result.succeeded


def test_allure_generation_archives_report_and_updates_history(tmp_path, monkeypatch):
    results = tmp_path / "results"
    archive = tmp_path / "reports"
    history_store = archive / ".history"
    results.mkdir()
    history_store.mkdir(parents=True)
    (results / "result.json").write_text("{}", encoding="utf-8")
    (history_store / "history.json").write_text("old", encoding="utf-8")
    calls = []
    monkeypatch.setattr(
        "utils.allure_report.shutil.which",
        lambda command: "C:/Tools/allure/bin/allure.bat",
    )

    def run(command, **kwargs):
        calls.append((command, kwargs))
        output = Path(command[command.index("-o") + 1])
        output.mkdir(parents=True, exist_ok=True)
        if "--single-file" not in command:
            generated_history = output / "history"
            generated_history.mkdir()
            (generated_history / "history.json").write_text("updated", encoding="utf-8")
        else:
            (output / "index.html").write_text("report", encoding="utf-8")
        return CompletedProcess(command, 0, stdout="generated", stderr="")

    monkeypatch.setattr("utils.allure_report.subprocess.run", run)

    result = generate_allure_report(results, archive, report_name="named-run")

    assert result.succeeded
    assert result.report_dir == archive / "named-run"
    assert (results / "history" / "history.json").read_text(encoding="utf-8") == "old"
    assert (history_store / "history.json").read_text(encoding="utf-8") == "updated"
    assert Path((archive / "latest.txt").read_text(encoding="utf-8")) == result.report_dir.resolve()
    assert calls[0][0] == [
        "C:/Tools/allure/bin/allure.bat",
        "generate",
        str(results),
        "--clean",
        "-o",
        str(archive / ".history-build"),
    ]
    assert calls[1][0] == [
        "C:/Tools/allure/bin/allure.bat",
        "generate",
        str(results),
        "--clean",
        "--single-file",
        "-o",
        str(archive / "named-run"),
    ]
    assert calls[1][1]["check"] is False


def test_existing_report_name_gets_numeric_suffix(tmp_path, monkeypatch):
    results = tmp_path / "results"
    archive = tmp_path / "reports"
    results.mkdir()
    (results / "result.json").write_text("{}", encoding="utf-8")
    (archive / "named-run").mkdir(parents=True)
    monkeypatch.setattr("utils.allure_report.shutil.which", lambda command: "allure")

    def run(command, **kwargs):
        output = Path(command[command.index("-o") + 1])
        output.mkdir(parents=True, exist_ok=True)
        return CompletedProcess(command, 0, stdout="generated", stderr="")

    monkeypatch.setattr("utils.allure_report.subprocess.run", run)

    result = generate_allure_report(results, archive, report_name="named-run")

    assert result.report_dir == archive / "named-run-2"
