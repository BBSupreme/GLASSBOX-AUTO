from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .v3 import SourceTrack


class ParityStatus(str, Enum):
    MATCH = "MATCH"
    DIFFERENCE = "DIFFERENCE"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class ParityFinding:
    finding_id: str
    topic: str
    source_track: SourceTrack
    status: ParityStatus
    observed: Any = None
    canonical: Any = None
    source_reference: str | None = None
    notes: str | None = None


def compare_exact(
    *,
    finding_id: str,
    topic: str,
    source_track: SourceTrack,
    observed: Any,
    canonical: Any,
    source_reference: str | None = None,
    notes: str | None = None,
) -> ParityFinding:
    return ParityFinding(
        finding_id=finding_id,
        topic=topic,
        source_track=source_track,
        status=ParityStatus.MATCH if observed == canonical else ParityStatus.DIFFERENCE,
        observed=observed,
        canonical=canonical,
        source_reference=source_reference,
        notes=notes,
    )


def compare_numeric(
    *,
    finding_id: str,
    topic: str,
    source_track: SourceTrack,
    observed: float,
    canonical: float,
    tolerance: float,
    source_reference: str | None = None,
    notes: str | None = None,
) -> ParityFinding:
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    difference = abs(float(observed) - float(canonical))
    return ParityFinding(
        finding_id=finding_id,
        topic=topic,
        source_track=source_track,
        status=ParityStatus.MATCH if difference <= tolerance else ParityStatus.DIFFERENCE,
        observed=observed,
        canonical=canonical,
        source_reference=source_reference,
        notes=notes,
    )


def unresolved(
    *,
    finding_id: str,
    topic: str,
    source_track: SourceTrack,
    observed: Any = None,
    canonical: Any = None,
    source_reference: str | None = None,
    notes: str,
) -> ParityFinding:
    if not notes:
        raise ValueError("UNRESOLVED parity findings require notes")
    return ParityFinding(
        finding_id=finding_id,
        topic=topic,
        source_track=source_track,
        status=ParityStatus.UNRESOLVED,
        observed=observed,
        canonical=canonical,
        source_reference=source_reference,
        notes=notes,
    )
