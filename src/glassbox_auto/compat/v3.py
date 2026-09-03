from __future__ import annotations

from enum import Enum


class SourceTrack(str, Enum):
    REVISION_A = "REVISION_A"
    RECOVERED_V3_2 = "RECOVERED_V3_2"
    RECONSTRUCTED_V3_2_1 = "RECONSTRUCTED_V3_2_1"


class CoverageStrategy(str, Enum):
    REVISION_A_WEIGHT = "REVISION_A_WEIGHT"
    RECOVERED_CRITICAL4 = "RECOVERED_CRITICAL4"


class HistoricalConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class HistoricalReadiness(str, Enum):
    READY = "READY"
    NEARLY_READY = "NEARLY_READY"
    NOT_READY = "NOT_READY"


V3_NEED_UTILITY = 0.8
V3_DIMENSION_BASE_WEIGHTS = {
    "economics": 35.0,
    "family": 25.0,
    "comfort": 15.0,
    "ev_usability": 15.0,
    "equipment_ux": 10.0,
}
V3_FAMILY_SUBWEIGHTS = {
    "baggage": 0.30,
    "by_fit": 0.25,
    "child_seat_stroller": 0.30,
    "child_protection": 0.15,
}
V3_RANGE_ANCHORS_KM = (200.0, 350.0, 500.0)
V3_DC_ANCHORS_MINUTES = (45.0, 28.0, 18.0)
V3_CHILD_PROTECTION_FLOOR = 70.0
V3_CHILD_PROTECTION_STRETCH = 95.0
V3_NCAP_MIN_STARS = 5
V3_NCAP_MIN_PROTOCOL_YEAR = 2020


def close_call_coverage(
    strategy: CoverageStrategy,
    *,
    weight_coverage: float | None = None,
    critical_verified: int | None = None,
    critical_total: int = 4,
) -> float:
    """Return coverage under one explicitly named historical strategy.

    REVISION_A_WEIGHT is the binding addendum rule. RECOVERED_CRITICAL4
    reproduces the later recovered workbook's observed four-check measure.
    The function intentionally refuses implicit strategy selection.
    """
    if strategy == CoverageStrategy.REVISION_A_WEIGHT:
        if weight_coverage is None:
            raise ValueError("REVISION_A_WEIGHT requires weight_coverage")
        if not 0.0 <= weight_coverage <= 1.0:
            raise ValueError("weight_coverage must be within [0, 1]")
        return float(weight_coverage)

    if critical_verified is None:
        raise ValueError("RECOVERED_CRITICAL4 requires critical_verified")
    if critical_total != 4:
        raise ValueError("RECOVERED_CRITICAL4 is defined only for the recovered four-check contract")
    if not 0 <= critical_verified <= critical_total:
        raise ValueError("critical_verified must be between 0 and critical_total")
    return critical_verified / critical_total


def critical4_confidence(critical_verified: int) -> HistoricalConfidence:
    """Observed recovered-v3 Confidence mapping from critical checks / 4."""
    coverage = close_call_coverage(
        CoverageStrategy.RECOVERED_CRITICAL4,
        critical_verified=critical_verified,
    )
    if coverage >= 0.85:
        return HistoricalConfidence.HIGH
    if coverage >= 0.50:
        return HistoricalConfidence.MEDIUM
    return HistoricalConfidence.LOW


def recovered_v3_readiness(
    *,
    open_critical_checks: int,
    expired_top_offer: bool = False,
) -> HistoricalReadiness:
    """Reproduce only the readiness rule stated in the recovered v3 handover.

    Implementation handover: 0 open -> READY, <=2 -> NEARLY READY,
    otherwise or EXPIRED -> NOT READY.

    This is deliberately named RECOVERED behavior. It is not presented as
    the Revision A readiness rule because Revision A frames readiness through
    decision-critical UNKNOWNs, close-call and freshness differently.
    """
    if open_critical_checks < 0 or open_critical_checks > 4:
        raise ValueError("open_critical_checks must be within [0, 4]")
    if expired_top_offer:
        return HistoricalReadiness.NOT_READY
    if open_critical_checks == 0:
        return HistoricalReadiness.READY
    if open_critical_checks <= 2:
        return HistoricalReadiness.NEARLY_READY
    return HistoricalReadiness.NOT_READY
