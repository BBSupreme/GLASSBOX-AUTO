import pytest

from glassbox_auto.engine import evaluate_candidate
from glassbox_auto.models import (
    AcquisitionMode,
    AcquisitionOffer,
    Criterion,
    Eligibility,
    Evidence,
    EvidenceGrade,
    GateDefinition,
    ObservedValue,
    PreferenceLabel,
    Readiness,
    UserProfile,
    UtilityAnchors,
    Vehicle,
)


def verified(value, unit=None):
    return ObservedValue(value, Evidence(EvidenceGrade.VERIFIED, source="decision-critical-test"), unit=unit)


def estimated(value, unit=None):
    return ObservedValue(value, Evidence(EvidenceGrade.ESTIMATED, source="decision-critical-estimate"), unit=unit)


def lease_offer(vehicle_id):
    return AcquisitionOffer(
        "offer",
        vehicle_id,
        AcquisitionMode.LEASE_NEW,
        currency="DKK",
        term_months=verified(36, "month"),
        annual_km=verified(15000, "km/year"),
        upfront_payment=verified(10000, "DKK"),
        recurring_payment=verified(4000, "DKK/month"),
        mandatory_fees=verified(1000, "DKK"),
        overage_cost_per_km=verified(2, "DKK/km"),
    )


def test_noncritical_unknown_does_not_block_eligibility_or_readiness():
    criteria = (
        Criterion(
            "noncritical_check",
            "optional_check",
            PreferenceLabel.MEDIUM,
            anchors=None,
            gate=GateDefinition(">=", 1, EvidenceGrade.VERIFIED, decision_critical=False),
            base_weight=0,
        ),
        Criterion("quality", "quality", PreferenceLabel.MEDIUM, UtilityAnchors(0, 5, 10, 0.8)),
    )
    profile = UserProfile("p", criteria, expected_annual_km=15000)
    vehicle = Vehicle(
        "v",
        "M",
        "X",
        "A",
        {"optional_check": estimated(1), "quality": verified(8)},
    )

    result = evaluate_candidate(vehicle, lease_offer("v"), profile)

    assert result.eligibility == Eligibility.ELIGIBLE
    assert result.readiness == Readiness.READY
    assert "decision_critical_unknown" not in result.reasons
    assert result.evidence_coverage < 1.0


def test_decision_critical_unknown_still_blocks_under_generic_policy():
    criteria = (
        Criterion(
            "critical_check",
            "critical_check",
            PreferenceLabel.MEDIUM,
            anchors=None,
            gate=GateDefinition(">=", 1, EvidenceGrade.VERIFIED, decision_critical=True),
            base_weight=0,
        ),
        Criterion("quality", "quality", PreferenceLabel.MEDIUM, UtilityAnchors(0, 5, 10, 0.8)),
    )
    profile = UserProfile("p", criteria, expected_annual_km=15000)
    vehicle = Vehicle("v", "M", "X", "A", {"critical_check": estimated(1), "quality": verified(8)})

    result = evaluate_candidate(vehicle, lease_offer("v"), profile)

    assert result.eligibility == Eligibility.BLOCKED
    assert result.readiness == Readiness.NOT_READY
    assert "decision_critical_unknown" in result.reasons


def test_must_have_gate_cannot_be_noncritical():
    with pytest.raises(ValueError, match="decision-critical"):
        Criterion(
            "must",
            "must",
            PreferenceLabel.MUST_HAVE,
            UtilityAnchors(0, 5, 10, 0.8),
            GateDefinition(">=", 5, EvidenceGrade.VERIFIED, decision_critical=False),
        )
