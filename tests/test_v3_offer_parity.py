from datetime import date, timedelta

from glassbox_auto.compat.v3_offers import (
    HistoricalFreshness,
    HistoricalGateResult,
    HistoricalOfferStatus,
    canonical_offer_gate,
    observed_recovered_v3_offer_gate,
    recovered_offer_freshness,
)


def test_recovered_freshness_marks_elapsed_valid_until_expired():
    freshness = recovered_offer_freshness(
        status=HistoricalOfferStatus.ACTIVE,
        control_date=date(2026, 8, 29),
        valid_until=date(2026, 9, 1),
        today=date(2026, 9, 3),
    )
    assert freshness == HistoricalFreshness.EXPIRED


def test_pc07_observed_workbook_passes_active_plus_expired_freshness():
    assert observed_recovered_v3_offer_gate(
        status=HistoricalOfferStatus.ACTIVE,
        freshness=HistoricalFreshness.EXPIRED,
    ) == HistoricalGateResult.PASS


def test_pc07_canonical_adapter_rejects_active_plus_expired_freshness():
    assert canonical_offer_gate(
        status=HistoricalOfferStatus.ACTIVE,
        freshness=HistoricalFreshness.EXPIRED,
    ) == HistoricalGateResult.FAIL


def test_stale_active_offer_is_check_in_both_tracks():
    assert observed_recovered_v3_offer_gate(
        status=HistoricalOfferStatus.ACTIVE,
        freshness=HistoricalFreshness.STALE,
    ) == HistoricalGateResult.CHECK
    assert canonical_offer_gate(
        status=HistoricalOfferStatus.ACTIVE,
        freshness=HistoricalFreshness.STALE,
    ) == HistoricalGateResult.CHECK


def test_freshness_boundary_is_strictly_greater_than_14_days():
    control = date(2026, 8, 20)
    assert recovered_offer_freshness(
        status=HistoricalOfferStatus.ACTIVE,
        control_date=control,
        today=control + timedelta(days=14),
    ) == HistoricalFreshness.FRESH
    assert recovered_offer_freshness(
        status=HistoricalOfferStatus.ACTIVE,
        control_date=control,
        today=control + timedelta(days=15),
    ) == HistoricalFreshness.STALE
