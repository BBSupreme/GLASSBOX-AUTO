from __future__ import annotations

from datetime import date
from enum import Enum


class HistoricalOfferStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRING = "EXPIRING"
    EXPIRED = "EXPIRED"
    HISTORICAL = "HISTORICAL"
    UNVERIFIED = "UNVERIFIED"


class HistoricalFreshness(str, Enum):
    FRESH = "FRESH"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    HISTORICAL = "HISTORICAL"


class HistoricalGateResult(str, Enum):
    PASS = "PASS"
    CHECK = "CHECK"
    FAIL = "FAIL"


def recovered_offer_freshness(
    *,
    status: HistoricalOfferStatus,
    control_date: date,
    today: date,
    valid_until: date | None = None,
    campaign_fresh_days: int = 14,
) -> HistoricalFreshness:
    """Reproduce the recovered Offers_Data freshness formula."""
    if campaign_fresh_days < 0:
        raise ValueError("campaign_fresh_days must be non-negative")
    if today < control_date:
        raise ValueError("today cannot be before control_date")
    if status == HistoricalOfferStatus.EXPIRED:
        return HistoricalFreshness.EXPIRED
    if status == HistoricalOfferStatus.HISTORICAL:
        return HistoricalFreshness.HISTORICAL
    if valid_until is not None and valid_until < today:
        return HistoricalFreshness.EXPIRED
    if (today - control_date).days > campaign_fresh_days:
        return HistoricalFreshness.STALE
    return HistoricalFreshness.FRESH


def observed_recovered_v3_offer_gate(
    *,
    status: HistoricalOfferStatus,
    freshness: HistoricalFreshness,
) -> HistoricalGateResult:
    """Reproduce Scoring_Engine!X exactly, including PC-07.

    For ACTIVE, the recovered formula checks only STALE. Thus an ACTIVE offer
    whose separately calculated freshness is EXPIRED returns PASS. This
    function exists only to make the observed regression testable.
    """
    if status == HistoricalOfferStatus.ACTIVE:
        return HistoricalGateResult.CHECK if freshness == HistoricalFreshness.STALE else HistoricalGateResult.PASS
    if status == HistoricalOfferStatus.EXPIRING:
        return HistoricalGateResult.CHECK
    return HistoricalGateResult.FAIL


def canonical_offer_gate(
    *,
    status: HistoricalOfferStatus,
    freshness: HistoricalFreshness,
) -> HistoricalGateResult:
    """Source-backed correction used by the compatibility layer.

    EXPIRED/HISTORICAL freshness cannot pass an active-offer gate. STALE or
    EXPIRING remains CHECK. Only ACTIVE+FRESH is PASS.
    """
    if freshness in {HistoricalFreshness.EXPIRED, HistoricalFreshness.HISTORICAL}:
        return HistoricalGateResult.FAIL
    if status == HistoricalOfferStatus.ACTIVE:
        return HistoricalGateResult.CHECK if freshness == HistoricalFreshness.STALE else HistoricalGateResult.PASS
    if status == HistoricalOfferStatus.EXPIRING:
        return HistoricalGateResult.CHECK
    return HistoricalGateResult.FAIL
