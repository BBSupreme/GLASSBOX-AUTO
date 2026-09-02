import pytest

from glassbox_auto.economics import PurchaseMethodBlockedError, lease_economics
from glassbox_auto.engine import close_call_threshold, evaluate_candidate, rank_candidates
from glassbox_auto.models import (
    AcquisitionMode,
    AcquisitionOffer,
    Criterion,
    Evidence,
    EvidenceGrade,
    GateDefinition,
    GateState,
    ObservedValue,
    PREFERENCE_MULTIPLIERS,
    PreferenceLabel,
    Readiness,
    UserProfile,
    UtilityAnchors,
    UtilityDirection,
    Vehicle,
)
from glassbox_auto.scoring import evaluate_gate, piecewise_utility, score_candidate


def obs(value, grade=EvidenceGrade.VERIFIED):
    return ObservedValue(value=value, evidence=Evidence(grade=grade, source="test"))


def test_binding_preference_multipliers():
    assert PREFERENCE_MULTIPLIERS == {
        PreferenceLabel.LOW: 0.5,
        PreferenceLabel.MEDIUM: 1.0,
        PreferenceLabel.HIGH: 1.5,
        PreferenceLabel.VERY_HIGH: 2.0,
        PreferenceLabel.MUST_HAVE: 2.0,
    }


def test_piecewise_higher_boundaries():
    a = UtilityAnchors(100, 200, 300)
    assert piecewise_utility(100, a) == 0
    assert piecewise_utility(200, a) == pytest.approx(0.8)
    assert piecewise_utility(300, a) == 1
    assert piecewise_utility(150, a) == pytest.approx(0.4)


def test_piecewise_lower_boundaries():
    a = UtilityAnchors(300, 200, 100, UtilityDirection.LOWER_IS_BETTER)
    assert piecewise_utility(300, a) == 0
    assert piecewise_utility(200, a) == pytest.approx(0.8)
    assert piecewise_utility(100, a) == 1


def test_missing_data_excluded_from_score_but_reduces_coverage():
    criteria = (
        Criterion("range", "range", PreferenceLabel.HIGH, UtilityAnchors(200, 400, 600)),
        Criterion("cargo", "cargo", PreferenceLabel.HIGH, UtilityAnchors(300, 500, 700)),
    )
    score, coverage, results = score_candidate(criteria, {"range": obs(600)})
    assert score == pytest.approx(10.0)
    assert coverage == pytest.approx(0.5)
    assert results[1].utility is None


def test_unknown_evidence_is_uncovered_and_unscored():
    criteria = (Criterion("range", "range", PreferenceLabel.HIGH, UtilityAnchors(200, 400, 600)),)
    score, coverage, _ = score_candidate(criteria, {"range": obs(600, EvidenceGrade.UNKNOWN)})
    assert score is None
    assert coverage == 0


def test_gate_pass_fail_unknown_and_evidence_threshold():
    gate = GateDefinition(">=", 500, EvidenceGrade.VERIFIED)
    assert evaluate_gate(obs(500), gate) == GateState.PASS
    assert evaluate_gate(obs(499), gate) == GateState.FAIL
    assert evaluate_gate(None, gate) == GateState.UNKNOWN
    assert evaluate_gate(obs(600, EvidenceGrade.ESTIMATED), gate) == GateState.UNKNOWN


def test_must_have_requires_gate():
    criteria = (Criterion("x", "x", PreferenceLabel.MUST_HAVE, UtilityAnchors(0, 1, 2)),)
    with pytest.raises(ValueError):
        score_candidate(criteria, {"x": obs(2)})


def test_close_call_boundary():
    assert close_call_threshold(0.949) == 0.20
    assert close_call_threshold(0.95) == 0.15


def test_lease_economics_reconciles_cash_and_mileage():
    offer = AcquisitionOffer(
        "o1", "v1", AcquisitionMode.LEASE_NEW,
        term_months=36, annual_km=15000,
        upfront_payment=10000, recurring_payment=4000, mandatory_fees=1000,
        overage_cost_per_km=2.0,
    )
    profile = UserProfile("p", (), expected_annual_km=20000)
    econ = lease_economics(offer, profile)
    assert econ["base_cash_cost"] == 155000
    assert econ["overage_cost"] == 30000
    assert econ["total_adjusted_cost"] == 185000


def test_unused_km_loss_only_when_assumption_supplied():
    offer = AcquisitionOffer("o1", "v1", AcquisitionMode.LEASE_NEW, term_months=36, annual_km=15000)
    no_value = lease_economics(offer, UserProfile("p", (), expected_annual_km=10000))
    with_value = lease_economics(offer, UserProfile("p", (), expected_annual_km=10000, unused_km_value_per_km=1.0))
    assert no_value["unused_km_value_loss"] == 0
    assert with_value["unused_km_value_loss"] == 15000


def test_purchase_economics_fail_closed():
    offer = AcquisitionOffer("o1", "v1", AcquisitionMode.BUY_NEW)
    with pytest.raises(PurchaseMethodBlockedError):
        lease_economics(offer, UserProfile("p", ()))


def test_failed_gate_blocks_readiness():
    vehicle = Vehicle("v1", "Make", "Model", "Variant", {"cargo": obs(400)})
    criterion = Criterion(
        "cargo", "cargo", PreferenceLabel.MUST_HAVE,
        UtilityAnchors(300, 500, 700), GateDefinition(">=", 500),
    )
    result = evaluate_candidate(
        vehicle,
        AcquisitionOffer("o1", "v1", AcquisitionMode.LEASE_NEW, term_months=36),
        UserProfile("p", (criterion,)),
    )
    assert result.readiness == Readiness.NOT_READY
    assert "failed_gate" in result.reasons


def test_deterministic_tie_uses_candidate_id():
    c = Criterion("range", "range", PreferenceLabel.HIGH, UtilityAnchors(200, 400, 600))
    profile = UserProfile("p", (c,))
    vehicle = Vehicle("v", "M", "X", "A", {"range": obs(500)})
    a = evaluate_candidate(vehicle, AcquisitionOffer("a", "v", AcquisitionMode.LEASE_NEW, term_months=36), profile)
    b = evaluate_candidate(vehicle, AcquisitionOffer("b", "v", AcquisitionMode.LEASE_NEW, term_months=36), profile)
    ranked = rank_candidates([b, a])
    assert ranked[0].candidate_id.endswith(":a")
    assert ranked[0].close_call is True
