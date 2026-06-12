"""Static AST extraction for ``@covers`` test metadata."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


class CoverageValidationError(ValueError):
    """Raised when a covers decorator cannot be statically validated."""


class TestCoverageExtractor(ast.NodeVisitor):
    """Extract literal ``@covers`` metadata without importing test modules."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.coverage_data: list[dict[str, Any]] = []
        self.errors: list[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_test_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_test_function(node)

    def _visit_test_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or self._decorator_name(decorator.func) != "covers":
                continue
            try:
                metadata = self._parse_decorator(decorator)
            except CoverageValidationError as error:
                self.errors.append(f"{self.file_path}:{node.lineno}: {error}")
                continue
            metadata["test_function"] = node.name
            metadata["file_path"] = self.file_path.as_posix()
            self.coverage_data.append(metadata)

    @staticmethod
    def _decorator_name(node: ast.expr) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return None

    @staticmethod
    def _parse_decorator(node: ast.Call) -> dict[str, Any]:
        if node.args:
            raise CoverageValidationError("@covers accepts keyword arguments only")

        metadata: dict[str, Any] = {}
        for keyword in node.keywords:
            if keyword.arg is None:
                raise CoverageValidationError("@covers does not support **kwargs")
            try:
                metadata[keyword.arg] = ast.literal_eval(keyword.value)
            except (ValueError, TypeError):
                raise CoverageValidationError(
                    f"@covers field '{keyword.arg}' must be a literal"
                ) from None

        missing = [field for field in ("type", "target") if not metadata.get(field)]
        if missing:
            raise CoverageValidationError(
                f"@covers missing mandatory field(s): {', '.join(missing)}"
            )
        if metadata["type"] not in {"ui", "api", "visual"}:
            raise CoverageValidationError(f"unsupported type: {metadata['type']}")
        metadata.setdefault("priority", "medium")
        metadata.setdefault("template", None)
        return metadata


def generate_coverage_map(
    test_dir: str | Path,
    output_json: str | Path | None = None,
    *,
    strict: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    """Scan tests and optionally write a target-indexed coverage map."""
    root = Path(test_dir)
    aggregated: dict[str, list[dict[str, Any]]] = {}
    errors: list[str] = []

    for file_path in sorted(root.rglob("*.py")):
        if not (file_path.name.startswith("test_") or file_path.name.endswith("_test.py")):
            continue
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        except SyntaxError as error:
            errors.append(f"{file_path}:{error.lineno}: {error.msg}")
            continue

        extractor = TestCoverageExtractor(file_path)
        extractor.visit(tree)
        errors.extend(extractor.errors)
        for item in extractor.coverage_data:
            target = item.pop("target")
            aggregated.setdefault(target, []).append(item)

    if strict and errors:
        raise CoverageValidationError("\n".join(errors))
    if output_json is not None:
        destination = Path(output_json)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(aggregated, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return aggregated
