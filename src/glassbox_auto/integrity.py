"""Numerical and identity guards for the canonical engine (policy v1).

These guards reject invalid arithmetic; they do not coerce it to UNKNOWN or
zero. The close-call tolerance is in score points, not display precision.
"""
from __future__ import annotations

from dataclasses import fields, is_dataclass
import math
from urllib.parse import quote

CLOSE_CALL_ABS_TOL = 1e-12


class NumericalIntegrityError(ValueError):
    """An input or computed numerical value cannot be represented safely."""


def require_finite(value: int | float, field_name: str) -> None:
    try:
        valid = (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        )
    except (OverflowError, ValueError, TypeError):
        valid = False
    if not valid:
        raise NumericalIntegrityError(f"{field_name} must be a finite number")


def require_range(value: int | float, low: float, high: float, field_name: str) -> None:
    require_finite(value, field_name)
    if not low <= value <= high:
        raise NumericalIntegrityError(f"{field_name} must be in [{low}, {high}]")


def require_finite_tree(value, field_name: str) -> None:
    """Check numeric leaves of engine-owned result structures before exposure."""
    if isinstance(value, bool) or value is None:
        return
    if isinstance(value, (int, float)):
        require_finite(value, field_name)
    elif is_dataclass(value) and not isinstance(value, type):
        for field in fields(value):
            require_finite_tree(getattr(value, field.name), f"{field_name}.{field.name}")
    elif isinstance(value, dict):
        for key, item in value.items():
            require_finite_tree(item, f"{field_name}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            require_finite_tree(item, f"{field_name}[{index}]")


def require_identifier(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError(f"{field_name} must be a non-empty identifier without control characters")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{field_name} must be a valid UTF-8 identifier") from exc


def make_candidate_id(vehicle_id: str, offer_id: str) -> str:
    """Percent-encode each component; preserve ordinary unreserved legacy IDs."""
    require_identifier(vehicle_id, "vehicle_id")
    require_identifier(offer_id, "offer_id")
    return f"{quote(vehicle_id, safe='')}:{quote(offer_id, safe='')}"


def is_close_call(score_a: float, score_b: float, threshold: float) -> bool:
    require_range(score_a, 0.0, 10.0, "score_a")
    require_range(score_b, 0.0, 10.0, "score_b")
    require_range(threshold, 0.0, 10.0, "threshold")
    gap = abs(score_a - score_b)
    return gap <= threshold or math.isclose(gap, threshold, rel_tol=0.0, abs_tol=CLOSE_CALL_ABS_TOL)
