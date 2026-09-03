import math
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
    Readiness,
    UserProfile,
    UtilityAnchors,
    Vehicle,
)


def verified(value, unit=None):
    return ObservedValue(value, Evidence(EvidenceGrade.VERIFIED, source="round2"), unit=unit)


def lease_offer(vehicle_id="v", annual_km=15000):
    return AcquisitionOffer(
        "offer",
        vehicle_id,
        AcquisitionMode.LEASE_NEW,
        currency="DKK",
        term_months=verified(36, "month"),
        annual_km=verified(annual_km, "km/year"),
        upfront_payment=verified(10000, "DKK"),
        recurring_payment=verified(4000, "DKK/month"),
        mandatory_fees=verified(1000, "DKK"),
        overage_cost_per_km=verified(2, "DKK/km"),
    )


def test_recovered_v3_can_explicitly_ignore_unused_km_in_economics():
    profile = UserProfile(
        "recovered-v3",
        (),
        expected_annual_km=9000,
        require_unused_km_value=False,
    )
    economics = lease_economics(lease_offer(), profile)

    assert economics["complete"] is True
    assert economics["unused_km_value_loss"] == 0.0
    assert economics["mileage_adjustment"] == 0.0
    assert economics["total_adjusted_cost"] == economics["base_cash_cost"]
    assert economics["derived_attributes"]["economics.total_adjusted_cost"].evidence.grade == EvidenceGrade.VERIFIED


def test_gate_only_numeric_string_is_unknown_not_false_pass_or_exception():
    criteria = (
        Criterion(
            "seats_gate",
            "seats",
            PreferenceLabel.MEDIUM,
            anchors=None,
            gate=GateDefinition(">=", 5, EvidenceGrade.VERIFIED),
            base_weight=0,
        ),
        Criterion("quality", "quality", PreferenceLabel.MEDIUM, UtilityAnchors(0, 5, 10, 0.8)),
    )
    profile = UserProfile("p", criteria, expected_annual_km=15000)
    vehicle = Vehicle("v", "M", "X", "A", {"seats": verified("5"), "quality": verified(8)})

    result = evaluate_candidate(vehicle, lease_offer(), profile)
    gate = next(item for item in result.criterion_results if item.criterion_id == "seats_gate")

    assert gate.gate_state == GateState.UNKNOWN
    assert gate.reason == "type_mismatch"
    assert result.eligibility == Eligibility.BLOCKED
    assert result.readiness == Readiness.NOT_READY


def test_nan_vehicle_metric_cannot_turn_into_maximum_utility():
    criterion = Criterion("range", "range", PreferenceLabel.HIGH, UtilityAnchors(200, 350, 500, 0.8))
    profile = UserProfile("p", (criterion,), expected_annual_km=15000)
    vehicle = Vehicle("v", "M", "X", "A", {"range": verified(float("nan"))})

    result = evaluate_candidate(vehicle, lease_offer(), profile)

    assert result.score is None
    assert result.criterion_results[0].reason == "type_mismatch"
    assert result.eligibility == Eligibility.BLOCKED


def test_nonfinite_offer_inputs_are_rejected():
    with pytest.raises(TypeError, match="finite"):
        AcquisitionOffer(
            "offer",
            "v",
            AcquisitionMode.LEASE_NEW,
            currency="DKK",
            term_months=verified(36, "month"),
            annual_km=verified(float("inf"), "km/year"),
            upfront_payment=verified(10000, "DKK"),
            recurring_payment=verified(4000, "DKK/month"),
            mandatory_fees=verified(1000, "DKK"),
        )


def test_zero_annual_km_contract_is_rejected():
    with pytest.raises(ValueError, match="annual_km must be > 0"):
        lease_offer(annual_km=0)


def test_duplicate_criterion_ids_are_rejected():
    first = Criterion("same", "a", PreferenceLabel.MEDIUM, UtilityAnchors(0, 5, 10, 0.8))
    second = Criterion("same", "b", PreferenceLabel.MEDIUM, UtilityAnchors(0, 5, 10, 0.8))
    with pytest.raises(ValueError, match="criterion_id"):
        UserProfile("p", (first, second), expected_annual_km=15000)


def test_nonfinite_weights_and_anchors_are_rejected():
    with pytest.raises(ValueError, match="finite"):
        Criterion("bad", "x", PreferenceLabel.MEDIUM, UtilityAnchors(0, 5, 10, 0.8), base_weight=float("nan"))
    with pytest.raises(ValueError, match="finite"):
        UtilityAnchors(0, 5, float("inf"), 0.8)
    with pytest.raises(ValueError, match="finite"):
        GateDefinition(">=", float("nan"))
