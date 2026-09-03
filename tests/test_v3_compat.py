import pytest

from glassbox_auto.compat.v3 import (
    CoverageStrategy,
    HistoricalConfidence,
    HistoricalReadiness,
    SourceTrack,
    V3_CHILD_PROTECTION_FLOOR,
    V3_CHILD_PROTECTION_STRETCH,
    V3_DC_ANCHORS_MINUTES,
    V3_DIMENSION_BASE_WEIGHTS,
    V3_FAMILY_SUBWEIGHTS,
    V3_NCAP_MIN_PROTOCOL_YEAR,
    V3_NCAP_MIN_STARS,
    V3_NEED_UTILITY,
    V3_RANGE_ANCHORS_KM,
    close_call_coverage,
    critical4_confidence,
    recovered_v3_readiness,
)


def test_source_tracks_are_explicit_and_distinct():
    assert SourceTrack.REVISION_A != SourceTrack.RECOVERED_V3_2


def test_recovered_revision_a_constants():
    assert V3_NEED_UTILITY == 0.8
    assert V3_DIMENSION_BASE_WEIGHTS == {
        "economics": 35.0,
        "family": 25.0,
        "comfort": 15.0,
        "ev_usability": 15.0,
        "equipment_ux": 10.0,
    }
    assert sum(V3_DIMENSION_BASE_WEIGHTS.values()) == 100.0
    assert V3_RANGE_ANCHORS_KM == (200.0, 350.0, 500.0)
    assert V3_DC_ANCHORS_MINUTES == (45.0, 28.0, 18.0)


def test_recovered_v3_family_and_ncap_constants():
    assert V3_FAMILY_SUBWEIGHTS == {
        "baggage": 0.30,
        "by_fit": 0.25,
        "child_seat_stroller": 0.30,
        "child_protection": 0.15,
    }
    assert sum(V3_FAMILY_SUBWEIGHTS.values()) == pytest.approx(1.0)
    assert V3_CHILD_PROTECTION_FLOOR == 70.0
    assert V3_CHILD_PROTECTION_STRETCH == 95.0
    assert V3_NCAP_MIN_STARS == 5
    assert V3_NCAP_MIN_PROTOCOL_YEAR == 2020


def test_revision_a_weight_coverage_is_independent_of_recovered_critical4():
    assert close_call_coverage(
        CoverageStrategy.REVISION_A_WEIGHT,
        weight_coverage=0.949,
    ) == pytest.approx(0.949)
    assert close_call_coverage(
        CoverageStrategy.RECOVERED_CRITICAL4,
        critical_verified=3,
    ) == pytest.approx(0.75)


def test_coverage_strategy_never_falls_back_implicitly():
    with pytest.raises(ValueError, match="weight_coverage"):
        close_call_coverage(CoverageStrategy.REVISION_A_WEIGHT)
    with pytest.raises(ValueError, match="critical_verified"):
        close_call_coverage(CoverageStrategy.RECOVERED_CRITICAL4)
    with pytest.raises(ValueError, match="four-check"):
        close_call_coverage(
            CoverageStrategy.RECOVERED_CRITICAL4,
            critical_verified=3,
            critical_total=5,
        )


def test_recovered_critical4_confidence_thresholds():
    assert critical4_confidence(0) == HistoricalConfidence.LOW
    assert critical4_confidence(1) == HistoricalConfidence.LOW
    assert critical4_confidence(2) == HistoricalConfidence.MEDIUM
    assert critical4_confidence(3) == HistoricalConfidence.MEDIUM
    assert critical4_confidence(4) == HistoricalConfidence.HIGH


def test_recovered_readiness_is_kept_separate_from_revision_a():
    assert recovered_v3_readiness(open_critical_checks=0) == HistoricalReadiness.READY
    assert recovered_v3_readiness(open_critical_checks=1) == HistoricalReadiness.NEARLY_READY
    assert recovered_v3_readiness(open_critical_checks=2) == HistoricalReadiness.NEARLY_READY
    assert recovered_v3_readiness(open_critical_checks=3) == HistoricalReadiness.NOT_READY
    assert recovered_v3_readiness(open_critical_checks=4) == HistoricalReadiness.NOT_READY
    assert recovered_v3_readiness(open_critical_checks=0, expired_top_offer=True) == HistoricalReadiness.NOT_READY


def test_recovered_readiness_rejects_invalid_counts():
    with pytest.raises(ValueError):
        recovered_v3_readiness(open_critical_checks=-1)
    with pytest.raises(ValueError):
        recovered_v3_readiness(open_critical_checks=5)
