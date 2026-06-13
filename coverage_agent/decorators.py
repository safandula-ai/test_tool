"""Runtime metadata used by the static coverage analyzer."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable, Literal, TypeVar


CoverageType = Literal["ui", "api", "visual"]
Priority = Literal["low", "medium", "high", "critical"]
Presence = Literal["deterministic", "ephemeral"]
F = TypeVar("F", bound=Callable[..., object])


@dataclass(frozen=True)
class CoverageMetadata:
    """Validated metadata attached to a test function."""

    type: CoverageType
    target: str
    priority: Priority = "medium"
    template: str | None = None
    page: str | None = None
    feature: str | None = None
    presence: Presence = "deterministic"


def covers(
    *,
    type: CoverageType,
    target: str,
    priority: Priority = "medium",
    template: str | None = None,
    page: str | None = None,
    feature: str | None = None,
    presence: Presence = "deterministic",
) -> Callable[[F], F]:
    """Mark a test as covering a UI target or API endpoint."""
    if type not in {"ui", "api", "visual"}:
        raise ValueError(f"Unsupported coverage type: {type}")
    if priority not in {"low", "medium", "high", "critical"}:
        raise ValueError(f"Unsupported coverage priority: {priority}")
    if presence not in {"deterministic", "ephemeral"}:
        raise ValueError(f"Unsupported coverage presence: {presence}")
    if not target.strip():
        raise ValueError("Coverage target cannot be empty")

    metadata = CoverageMetadata(
        type, target.strip(), priority, template, page, feature, presence
    )

    def decorator(function: F) -> F:
        entries = list(getattr(function, "__coverage__", ()))
        entries.append(asdict(metadata))
        setattr(function, "__coverage__", tuple(entries))
        return function

    return decorator
