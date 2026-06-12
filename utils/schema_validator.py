from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


def load_schema(path: Path) -> dict:
    """Load a JSON schema from disk."""
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def validate(instance: object, schema: dict) -> None:
    """Validate an object against a JSON schema."""
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(instance)
