from __future__ import annotations

from enum import Enum
from math import isfinite

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


def _lineage(inputs: tuple[ObservedValue | None, ...]) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            source
            for value in inputs
            if value is not None
            for source in ((value.evidence.source,) + value.evidence.lineage)
            if source
        )
    )


def _derived_evidence(method: str, inputs: tuple[ObservedValue, ...]) -> Evidence:
    if not inputs or any(value.value is None for value in inputs):
        grade = EvidenceGrade.UNKNOWN
    else:
        grade = min((value.evidence.grade for value in inputs), key=lambda item: GRADE_RANK[item])
    return Evidence(
        grade=grade,
        source=f"derived:{method}",
        kind=EvidenceKind.DERIVED,
        method=method,
        lineage=_lineage(inputs),
    )


def _unknown_derived(method: str, inputs: tuple[ObservedValue | None, ...]) -> ObservedValue:
    return ObservedValue(
        None,
        Evidence(
            EvidenceGrade.UNKNOWN,
            source=f"derived:{method}",
            kind=EvidenceKind.DERIVED,
            method=method,
            lineage=_lineage(inputs),
        ),
    )


def _finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(float(value))


def derive_ncap_gate(
    protocol_year: ObservedValue | None,
    stars: ObservedValue | None,
) -> ObservedValue:
    """Canonical recovered-v3 NCAP composite: year>=2020 AND stars>=5."""
    raw_inputs = (protocol_year, stars)
    if protocol_year is None or stars is None or protocol_year.value is None or stars.value is None:
        return _unknown_derived("recovered_v3_ncap_gate", raw_inputs)
    if not _finite_number(protocol_year.value) or not _finite_number(stars.value):
        return _unknown_derived("recovered_v3_ncap_gate", raw_inputs)

    inputs = (protocol_year, stars)
    evidence = _derived_evidence("recovered_v3_ncap_gate", inputs)
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
    binding_period_months: int | float | None,
    max_binding_period_months: int | float | None,
    minimum_price_in_binding: float | None,
    termination_terms_known: bool,
    return_terms_known: bool,
) -> HistoricalCheck:
    """Revision A operationalization of acceptable lease terms.

    Required evidence is a concrete binding period, the user's maximum
    acceptable binding period, known minimum price in binding, and known
    termination/return terms. Missing or non-finite required evidence is
    UNKNOWN. A known binding-period breach or non-positive minimum price is
    FAIL.
    """
    if binding_period_months is None or max_binding_period_months is None or minimum_price_in_binding is None:
        return HistoricalCheck.UNKNOWN
    if not termination_terms_known or not return_terms_known:
        return HistoricalCheck.UNKNOWN
    if not _finite_number(binding_period_months):
        return HistoricalCheck.UNKNOWN
    if not _finite_number(max_binding_period_months):
        return HistoricalCheck.UNKNOWN
    if not _finite_number(minimum_price_in_binding):
        return HistoricalCheck.UNKNOWN
    if binding_period_months <= 0 or max_binding_period_months <= 0:
        return HistoricalCheck.UNKNOWN
    if binding_period_months > max_binding_period_months or minimum_price_in_binding <= 0:
        return HistoricalCheck.FAIL
    return HistoricalCheck.PASS
