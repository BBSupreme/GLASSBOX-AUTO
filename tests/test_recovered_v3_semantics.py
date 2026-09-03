import pytest

from glassbox_auto.engine import evaluate_candidate, rank_candidates
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
from glassbox_auto.scoring import piecewise_utility


def verified(value, unit=None):
    return ObservedValue(value, Evidence(EvidenceGrade.VERIFIED, source="recovered-v3-fixture"), unit=unit)


def estimated(value, unit=None):
    return ObservedValue(value, Evidence(EvidenceGrade.ESTIMATED, source="recovered-v3-estimate"), unit=unit)


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


def test_revision_a_need_is_eight_of_ten():
    anchors = UtilityAnchors(200, 350, 500, 0.8)
    assert piecewise_utility(350, anchors) == pytest.approx(0.8)


def test_recovered_v3_unknown_gate_remains_ranked_but_not_ready():
    criteria = (
        Criterion(
            "ncap_gate",
            "ncap_stars",
            PreferenceLabel.MEDIUM,
            anchors=None,
            gate=GateDefinition(">=", 5, EvidenceGrade.VERIFIED),
            base_weight=0,
        ),
        Criterion(
            "quality",
            "quality",
            PreferenceLabel.MEDIUM,
            UtilityAnchors(0, 5, 10, 0.8),
        ),
    )
    profile = UserProfile("recovered-v3", criteria, expected_annual_km=15000)

    unknown_vehicle = Vehicle(
        "unknown",
        "M",
        "Unknown gate",
        "A",
        {"ncap_stars": estimated(5), "quality": verified(10)},
    )
    passed_vehicle = Vehicle(
        "passed",
        "M",
        "Passed gate",
        "A",
        {"ncap_stars": verified(5), "quality": verified(8)},
    )

    unknown = evaluate_candidate(
        unknown_vehicle,
        lease_offer("unknown"),
        profile,
        unknown_gate_blocks_eligibility=False,
    )
    passed = evaluate_candidate(
        passed_vehicle,
        lease_offer("passed"),
        profile,
        unknown_gate_blocks_eligibility=False,
    )

    unknown_gate = next(r for r in unknown.criterion_results if r.criterion_id == "ncap_gate")
    assert unknown_gate.gate_state == GateState.UNKNOWN
    assert unknown.eligibility == Eligibility.ELIGIBLE
    assert unknown.readiness == Readiness.NOT_READY
    assert "decision_critical_unknown" in unknown.reasons

    ranked = rank_candidates([passed, unknown])
    assert ranked[0].vehicle_id == "unknown"
    assert ranked[0].eligibility == Eligibility.ELIGIBLE
    assert ranked[0].readiness == Readiness.NOT_READY


def test_recovered_v3_fail_gate_is_ineligible():
    criteria = (
        Criterion(
            "seats_gate",
            "seats",
            PreferenceLabel.MEDIUM,
            anchors=None,
            gate=GateDefinition(">=", 5, EvidenceGrade.ESTIMATED),
            base_weight=0,
        ),
        Criterion("quality", "quality", PreferenceLabel.MEDIUM, UtilityAnchors(0, 5, 10, 0.8)),
    )
    profile = UserProfile("recovered-v3", criteria, expected_annual_km=15000)
    vehicle = Vehicle("failed", "M", "Failed gate", "A", {"seats": verified(4), "quality": verified(10)})

    result = evaluate_candidate(
        vehicle,
        lease_offer("failed"),
        profile,
        unknown_gate_blocks_eligibility=False,
    )

    assert result.eligibility == Eligibility.FAILED
    assert result.readiness == Readiness.NOT_READY
