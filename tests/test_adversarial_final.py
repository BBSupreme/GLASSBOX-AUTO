import pytest

from glassbox_auto.economics import lease_economics
from glassbox_auto.engine import evaluate_candidate
from glassbox_auto.models import (
    AcquisitionMode,
    AcquisitionOffer,
    Criterion,
    Eligibility,
    Evidence,
    EvidenceGrade,
    GateDefinition,
    GateState,
    ObservedValue,
    PreferenceLabel,
    UserProfile,
    UtilityAnchors,
    Vehicle,
)


def verified(value, unit=None):
    return ObservedValue(
        value,
        Evidence(EvidenceGrade.VERIFIED, source="final-falsifier"),
        unit=unit,
    )


def lease_offer():
    return AcquisitionOffer(
        "o",
        "v",
        AcquisitionMode.LEASE_NEW,
        currency="DKK",
        term_months=verified(36, "month"),
        annual_km=verified(15000, "km/year"),
        upfront_payment=verified(10000, "DKK"),
        recurring_payment=verified(4000, "DKK/month"),
        mandatory_fees=verified(1000, "DKK"),
        overage_cost_per_km=verified(2.0, "DKK/km"),
    )


def test_unused_km_assumption_wrong_currency_unit_is_unknown():
    profile = UserProfile(
        "p",
        (),
        expected_annual_km=10000,
        unused_km_value_per_km=verified(1.0, "EUR/km"),
    )
    economics = lease_economics(lease_offer(), profile)

    assert economics["unused_km_value_loss"] is None
    assert economics["total_adjusted_cost"] is None
    assert economics["complete"] is False
    assert "unused_km_value_per_km_unit_mismatch" in economics["reasons"]


def test_numeric_string_is_not_silently_coerced_for_utility_or_gate():
    criterion = Criterion(
        "range",
        "range",
        PreferenceLabel.MUST_HAVE,
        UtilityAnchors(200, 400, 600, 0.8),
        GateDefinition(">=", 400),
        unit="km",
    )
    profile = UserProfile("p", (criterion,), expected_annual_km=15000)
    vehicle = Vehicle("v", "M", "X", "A", {"range": verified("500", "km")})

    result = evaluate_candidate(vehicle, lease_offer(), profile)

    assert result.eligibility == Eligibility.BLOCKED
    assert "type_mismatch" in result.reasons
    assert "decision_critical_unknown" in result.reasons
    assert result.criterion_results[0].reason == "type_mismatch"
    assert result.criterion_results[0].gate_state == GateState.UNKNOWN
    assert result.score is None
