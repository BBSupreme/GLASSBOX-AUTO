from __future__ import annotations

from enum import Enum

from glassbox_auto.models import Evidence, EvidenceGrade, EvidenceKind, GRADE_RANK, ObservedValue

from .v3 import V3_NCAP_MIN_PROTOCOL_YEAR, V3_NCAP_MIN_STARS


class HistoricalCheck(str, Enum):
    PASS = "PASS"
    CHECK = "CHECK"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    TO_TEST = "TO TEST"


class FamilyTestState(str, Enum):
    PASS = "PASS"
    CONCERN = "CONCERN"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


def _derived_evidence(method: str, inputs: tuple[ObservedValue, ...]) -> Evidence:
    usable = tuple(value for value in inputs if value is not None)
    if not usable or any(value.value is None for value in usable):
        grade = EvidenceGrade.UNKNOWN
    else:
        grade = min((value.evidence.grade for value in usable), key=lambda item: GRADE_RANK[item])
    lineage = tuple(
        dict.fromkeys(
            source
            for value in usable
            for source in ((value.evidence.source,) + value.evidence.lineage)
            if source
        )
    )
    return Evidence(
        grade=grade,
        source=f"derived:{method}",
        kind=EvidenceKind.DERIVED,
        method=method,
        lineage=lineage,
    )


def derive_ncap_gate(
    protocol_year: ObservedValue | None,
    stars: ObservedValue | None,
) -> ObservedValue:
    """Canonical recovered-v3 NCAP composite: year>=2020 AND stars>=5."""
    inputs = tuple(value for value in (protocol_year, stars) if value is not None)
    evidence = _derived_evidence("recovered_v3_ncap_gate", inputs)
    if protocol_year is None or stars is None or protocol_year.value is None or stars.value is None:
        return ObservedValue(None, evidence)
    if not isinstance(protocol_year.value, (int, float)) or isinstance(protocol_year.value, bool):
        return ObservedValue(None, Evidence(EvidenceGrade.UNKNOWN, source="derived:recovered_v3_ncap_gate", kind=EvidenceKind.DERIVED, method="recovered_v3_ncap_gate", lineage=evidence.lineage))
    if not isinstance(stars.value, (int, float)) or isinstance(stars.value, bool):
        return ObservedValue(None, Evidence(EvidenceGrade.UNKNOWN, source="derived:recovered_v3_ncap_gate", kind=EvidenceKind.DERIVED, method="recovered_v3_ncap_gate", lineage=evidence.lineage))
    value = protocol_year.value >= V3_NCAP_MIN_PROTOCOL_YEAR and stars.value >= V3_NCAP_MIN_STARS
    return ObservedValue(value, evidence)


def canonical_family_gate(
    *,
    dealbreaker: bool,
    child_seat: FamilyTestState,
    stroller: FamilyTestState,
) -> HistoricalCheck:
    if dealbreaker:
        return HistoricalCheck.FAIL
    if FamilyTestState.FAIL in {child_seat, stroller}:
        return HistoricalCheck.FAIL
    if child_seat == FamilyTestState.PASS and stroller == FamilyTestState.PASS:
        return HistoricalCheck.PASS
    if FamilyTestState.CONCERN in {child_seat, stroller}:
        return HistoricalCheck.CHECK
    return HistoricalCheck.TO_TEST


def observed_recovered_v3_family_gate(
    *,
    date_field: str | None,
    child_seat: FamilyTestState,
    stroller: FamilyTestState,
) -> HistoricalCheck:
    """Reproduce recovered Scoring_Engine!Y, including PC-08 row error."""
    if date_field == "YES":
        return HistoricalCheck.FAIL
    if FamilyTestState.FAIL in {child_seat, stroller}:
        return HistoricalCheck.FAIL
    if child_seat == FamilyTestState.PASS and stroller == FamilyTestState.PASS:
        return HistoricalCheck.PASS
    if FamilyTestState.CONCERN in {child_seat, stroller}:
        return HistoricalCheck.CHECK
    return HistoricalCheck.TO_TEST


def observed_recovered_v3_terms_gate(*, minimum_price_in_binding: float | None) -> HistoricalCheck:
    """Reproduce Scoring_Engine!Z: only minimum price is checked."""
    return HistoricalCheck.PASS if minimum_price_in_binding is not None and minimum_price_in_binding > 0 else HistoricalCheck.UNKNOWN


def canonical_terms_gate(
    *,
    binding_period_known: bool,
    minimum_price_in_binding: float | None,
    termination_terms_known: bool,
    return_terms_known: bool,
) -> HistoricalCheck:
    """Revision A operationalization of acceptable lease terms.

    This layer checks evidence completeness, not whether the user's maximum
    binding-period preference is satisfied; that threshold comparison remains
    a separate explicit criterion/gate input.
    """
    if minimum_price_in_binding is None or minimum_price_in_binding <= 0:
        return HistoricalCheck.UNKNOWN
    if not binding_period_known or not termination_terms_known or not return_terms_known:
        return HistoricalCheck.UNKNOWN
    return HistoricalCheck.PASS
