import pytest

from glassbox_auto.economics import PurchaseMethodBlockedError, lease_economics
from glassbox_auto.engine import close_call_threshold, evaluate_candidate, rank_candidates
from glassbox_auto.models import (
    AcquisitionMode,
    AcquisitionOffer,
    Criterion,
    Eligibility,
    Evidence,
    EvidenceGrade,
    EvidenceKind,
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


def obs(value, grade=EvidenceGrade.VERIFIED, *, unit=None, kind=EvidenceKind.DIRECT):
    source = "test" if grade == EvidenceGrade.VERIFIED else "test-estimate"
    return ObservedValue(value=value, evidence=Evidence(grade=grade, source=source, kind=kind), unit=unit)


def lease_offer(
    offer_id="o1",
    vehicle_id="v1",
    *,
    monthly=4000,
    annual_km=15000,
    overage=2.0,
    upfront=10000,
    fees=1000,
    currency="DKK",
):
    return AcquisitionOffer(
        offer_id,
        vehicle_id,
        AcquisitionMode.LEASE_NEW,
        currency=currency,
        term_months=obs(36, unit="month"),
        annual_km=obs(annual_km, unit="km/year"),
        upfront_payment=obs(upfront, unit=currency),
        recurring_payment=obs(monthly, unit=f"{currency}/month"),
        mandatory_fees=obs(fees, unit=currency),
        overage_cost_per_km=obs(overage, unit=f"{currency}/km") if overage is not None else None,
    )


def anchors(floor=200, need=400, stretch=600, need_utility=0.8, direction=UtilityDirection.HIGHER_IS_BETTER):
    return UtilityAnchors(floor, need, stretch, need_utility, direction)


def test_binding_preference_multipliers():
    assert PREFERENCE_MULTIPLIERS == {
        PreferenceLabel.LOW: 0.5,
        PreferenceLabel.MEDIUM: 1.0,
        PreferenceLabel.HIGH: 1.5,
        PreferenceLabel.VERY_HIGH: 2.0,
        PreferenceLabel.MUST_HAVE: 2.0,
    }


def test_need_utility_is_explicit_and_changes_curve():
    a = anchors(100, 200, 300, 0.6)
    assert piecewise_utility(200, a) == pytest.approx(0.6)
    assert piecewise_utility(150, a) == pytest.approx(0.3)
    with pytest.raises(TypeError):
        UtilityAnchors(100, 200, 300)


def test_piecewise_lower_boundaries():
    a = anchors(300, 200, 100, 0.75, UtilityDirection.LOWER_IS_BETTER)
    assert piecewise_utility(300, a) == 0
    assert piecewise_utility(200, a) == pytest.approx(0.75)
    assert piecewise_utility(100, a) == 1


def test_missing_data_excluded_from_score_but_reduces_coverage():
    criteria = (
        Criterion("range", "range", PreferenceLabel.HIGH, anchors()),
        Criterion("cargo", "cargo", PreferenceLabel.HIGH, anchors(300, 500, 700)),
    )
    score, data_coverage, evidence_coverage, results = score_candidate(criteria, {"range": obs(600)})
    assert score == pytest.approx(10.0)
    assert data_coverage == pytest.approx(0.5)
    assert evidence_coverage == pytest.approx(0.5)
    assert results[1].utility is None


def test_insufficient_evidence_not_counted_as_decision_sufficient_coverage():
    criteria = (
        Criterion("range", "range", PreferenceLabel.HIGH, anchors(), minimum_evidence=EvidenceGrade.VERIFIED),
    )
    score, data_coverage, evidence_coverage, _ = score_candidate(
        criteria,
        {"range": obs(600, EvidenceGrade.ESTIMATED)},
    )
    assert score is None
    assert data_coverage == 1.0
    assert evidence_coverage == 0.0


def test_inactive_weight_remains_visible():
    criteria = (
        Criterion("active", "a", PreferenceLabel.HIGH, anchors()),
        Criterion("inactive", "b", PreferenceLabel.VERY_HIGH, anchors(), active=False),
    )
    _, _, _, results = score_candidate(criteria, {"a": obs(600), "b": obs(600)})
    assert len(results) == 2
    assert results[1].active is False
    assert results[1].reason == "inactive"
    assert results[1].normalized_weight == 0.0


def test_explicit_weighting_supports_dimensions_subweights_and_caps():
    criteria = (
        Criterion("baggage_main", "a", PreferenceLabel.MEDIUM, anchors(), dimension="family", base_weight=8),
        Criterion("baggage_extra", "b", PreferenceLabel.MEDIUM, anchors(), dimension="family", base_weight=2),
        Criterion("safety", "s", PreferenceLabel.MEDIUM, anchors(), dimension="family", base_weight=10, weight_cap=3),
    )
    profile = UserProfile("p", criteria, dimension_weights={"family": 2.0})
    _, _, _, results = score_candidate(criteria, {"a": obs(600), "b": obs(600), "s": obs(600)}, profile.dimension_weights)
    weights = {r.criterion_id: r.weight for r in results}
    assert weights["baggage_main"] == 16
    assert weights["baggage_extra"] == 4
    assert weights["safety"] == 3


def test_gate_pass_fail_unknown_and_evidence_threshold():
    gate = GateDefinition(">=", 500, EvidenceGrade.VERIFIED)
    assert evaluate_gate(obs(500), gate) == GateState.PASS
    assert evaluate_gate(obs(499), gate) == GateState.FAIL
    assert evaluate_gate(None, gate) == GateState.UNKNOWN
    assert evaluate_gate(obs(600, EvidenceGrade.ESTIMATED), gate) == GateState.UNKNOWN


def test_must_have_cannot_be_gate_only():
    with pytest.raises(ValueError):
        Criterion("x", "x", PreferenceLabel.MUST_HAVE, gate=GateDefinition(">=", 1))


def test_positive_weight_unscored_criterion_rejected_but_zero_weight_gate_allowed():
    with pytest.raises(ValueError):
        Criterion("dead", "x", PreferenceLabel.MEDIUM)
    gate_only = Criterion("gate", "x", PreferenceLabel.MEDIUM, gate=GateDefinition(">=", 1), base_weight=0)
    assert gate_only.base_weight == 0


def test_modeled_evidence_cannot_be_verified_and_verified_requires_source():
    with pytest.raises(ValueError):
        Evidence(EvidenceGrade.VERIFIED)
    with pytest.raises(ValueError):
        Evidence(EvidenceGrade.VERIFIED, source="model", kind=EvidenceKind.MODELED)


def test_close_call_boundary():
    assert close_call_threshold(0.949) == 0.20
    assert close_call_threshold(0.95) == 0.15


def test_lease_economics_reconciles_cash_and_mileage():
    offer = lease_offer()
    profile = UserProfile("p", (), expected_annual_km=20000)
    econ = lease_economics(offer, profile)
    assert econ["base_cash_cost"] == 155000
    assert econ["overage_cost"] == 30000
    assert econ["total_adjusted_cost"] == 185000
    assert econ["complete"] is True


def test_scenario_adjusted_economics_is_estimated_and_has_lineage():
    econ = lease_economics(lease_offer(), UserProfile("p", (), expected_annual_km=20000))
    derived = econ["derived_attributes"]["economics.total_adjusted_cost"]
    assert derived.evidence.grade == EvidenceGrade.ESTIMATED
    assert derived.evidence.kind == EvidenceKind.DERIVED
    assert "user_profile.expected_annual_km" in derived.evidence.lineage
    assert "test" in derived.evidence.lineage


def test_missing_overage_pricing_is_unknown_not_zero():
    offer = lease_offer(overage=None)
    econ = lease_economics(offer, UserProfile("p", (), expected_annual_km=20000))
    assert econ["overage_cost"] is None
    assert econ["total_adjusted_cost"] is None
    assert econ["complete"] is False
    assert "overage_cost_per_km_missing" in econ["reasons"]


def test_missing_unused_km_assumption_is_unknown_not_zero():
    offer = lease_offer()
    econ = lease_economics(offer, UserProfile("p", (), expected_annual_km=10000))
    assert econ["unused_km_value_loss"] is None
    assert econ["total_adjusted_cost"] is None
    assert "unused_km_value_per_km_missing" in econ["reasons"]


def test_unknown_economic_evidence_blocks_completeness():
    unknown = ObservedValue(4000, Evidence(EvidenceGrade.UNKNOWN), unit="DKK/month")
    offer = AcquisitionOffer(
        "o",
        "v",
        AcquisitionMode.LEASE_NEW,
        term_months=obs(36, unit="month"),
        annual_km=obs(15000, unit="km/year"),
        upfront_payment=obs(10000, unit="DKK"),
        recurring_payment=unknown,
        mandatory_fees=obs(1000, unit="DKK"),
        overage_cost_per_km=obs(2, unit="DKK/km"),
    )
    econ = lease_economics(offer, UserProfile("p", (), expected_annual_km=15000))
    assert econ["complete"] is False
    assert "recurring_payment_evidence_unknown" in econ["reasons"]


def test_purchase_economics_fail_closed():
    offer = AcquisitionOffer("o1", "v1", AcquisitionMode.BUY_NEW)
    with pytest.raises(PurchaseMethodBlockedError):
        lease_economics(offer, UserProfile("p", ()))


def test_economics_enters_canonical_scoring_and_changes_ranking():
    economic = Criterion(
        "cost",
        "economics.total_adjusted_cost",
        PreferenceLabel.HIGH,
        anchors(250000, 180000, 120000, 0.8, UtilityDirection.LOWER_IS_BETTER),
        unit="DKK",
    )
    profile = UserProfile("p", (economic,), expected_annual_km=15000)
    vehicle = Vehicle("v1", "M", "X", "A")
    cheap = evaluate_candidate(vehicle, lease_offer("cheap", monthly=3000), profile)
    expensive = evaluate_candidate(vehicle, lease_offer("expensive", monthly=5000), profile)
    ranked = rank_candidates([expensive, cheap])
    assert ranked[0].offer_id == "cheap"
    assert cheap.score > expensive.score


def test_criterion_unit_mismatch_blocks_candidate():
    criterion = Criterion("range", "range", PreferenceLabel.HIGH, anchors(), unit="km")
    profile = UserProfile("p", (criterion,), expected_annual_km=15000)
    vehicle = Vehicle("v", "M", "X", "A", {"range": obs(500, unit="mi")})
    result = evaluate_candidate(vehicle, lease_offer("o", "v"), profile)
    assert result.eligibility == Eligibility.BLOCKED
    assert "unit_mismatch" in result.reasons
    assert result.criterion_results[0].reason == "unit_mismatch"


def test_unknown_gate_candidate_cannot_outrank_pass_candidate():
    criterion = Criterion(
        "cargo",
        "cargo",
        PreferenceLabel.MUST_HAVE,
        anchors(300, 500, 700),
        GateDefinition(">=", 500, EvidenceGrade.VERIFIED),
    )
    profile = UserProfile("p", (criterion,), expected_annual_km=15000)
    pass_vehicle = Vehicle("pass", "M", "X", "A", {"cargo": obs(600)})
    unknown_vehicle = Vehicle("unknown", "M", "X", "A", {"cargo": obs(700, EvidenceGrade.ESTIMATED)})
    passed = evaluate_candidate(pass_vehicle, lease_offer("o", "pass"), profile)
    unknown = evaluate_candidate(unknown_vehicle, lease_offer("o", "unknown"), profile)
    ranked = rank_candidates([unknown, passed])
    assert passed.eligibility == Eligibility.ELIGIBLE
    assert unknown.eligibility == Eligibility.BLOCKED
    assert ranked[0].candidate_id.startswith("pass:")


def test_purchase_blocked_candidate_cannot_rank_first():
    c = Criterion("range", "range", PreferenceLabel.HIGH, anchors())
    profile = UserProfile("p", (c,), expected_annual_km=15000)
    vehicle = Vehicle("v", "M", "X", "A", {"range": obs(500)})
    lease = evaluate_candidate(vehicle, lease_offer("lease", "v"), profile)
    purchase = evaluate_candidate(vehicle, AcquisitionOffer("buy", "v", AcquisitionMode.BUY_NEW), profile)
    ranked = rank_candidates([purchase, lease])
    assert purchase.eligibility == Eligibility.BLOCKED
    assert ranked[0].offer_id == "lease"


def test_failed_candidate_cannot_create_close_call():
    c = Criterion("cargo", "cargo", PreferenceLabel.MUST_HAVE, anchors(300, 500, 700), GateDefinition(">=", 500))
    profile = UserProfile("p", (c,), expected_annual_km=15000)
    leader = evaluate_candidate(Vehicle("a", "M", "X", "A", {"cargo": obs(600)}), lease_offer("o", "a"), profile)
    failed = evaluate_candidate(Vehicle("b", "M", "X", "A", {"cargo": obs(499)}), lease_offer("o", "b"), profile)
    ranked = rank_candidates([leader, failed])
    assert ranked[0].close_call is False
    assert failed.eligibility == Eligibility.FAILED


def test_three_eligible_candidates_within_band_are_all_close_call():
    c = Criterion("score", "score", PreferenceLabel.HIGH, anchors(0, 5, 10, 0.8))
    profile = UserProfile("p", (c,), expected_annual_km=15000)
    results = []
    for vid, value in [("a", 9.00), ("b", 8.90), ("c", 8.85)]:
        vehicle = Vehicle(vid, "M", "X", "A", {"score": obs(value)})
        results.append(evaluate_candidate(vehicle, lease_offer("o", vid), profile))
    ranked = rank_candidates(results)
    assert all(candidate.close_call for candidate in ranked[:3])
    assert all(candidate.readiness == Readiness.NOT_READY for candidate in ranked[:3])


def test_ranking_recomputes_close_call_state_idempotently():
    c = Criterion("range", "range", PreferenceLabel.HIGH, anchors())
    profile = UserProfile("p", (c,), expected_annual_km=15000)
    vehicle = Vehicle("v", "M", "X", "A", {"range": obs(500)})
    a = evaluate_candidate(vehicle, lease_offer("a", "v"), profile)
    b = evaluate_candidate(vehicle, lease_offer("b", "v"), profile)
    first = rank_candidates([a, b])
    assert first[0].close_call is True
    reranked = rank_candidates([first[0]])
    assert reranked[0].close_call is False
    assert reranked[0].readiness == Readiness.READY
    assert "close_call" not in reranked[0].reasons


def test_offer_vehicle_attribute_collision_rejected():
    vehicle = Vehicle("v", "M", "X", "A", {"range": obs(500)})
    offer = AcquisitionOffer(
        "o",
        "v",
        AcquisitionMode.LEASE_NEW,
        term_months=obs(36, unit="month"),
        annual_km=obs(15000, unit="km/year"),
        upfront_payment=obs(10000, unit="DKK"),
        recurring_payment=obs(4000, unit="DKK/month"),
        mandatory_fees=obs(1000, unit="DKK"),
        overage_cost_per_km=obs(2, unit="DKK/km"),
        attributes={"range": obs(600)},
    )
    with pytest.raises(ValueError, match="collision"):
        evaluate_candidate(vehicle, offer, UserProfile("p", (Criterion("range", "range", PreferenceLabel.HIGH, anchors()),), expected_annual_km=15000))


def test_negative_economics_inputs_rejected():
    with pytest.raises(ValueError):
        AcquisitionOffer(
            "o",
            "v",
            AcquisitionMode.LEASE_NEW,
            term_months=obs(36, unit="month"),
            upfront_payment=obs(0, unit="DKK"),
            recurring_payment=obs(-1, unit="DKK/month"),
            mandatory_fees=obs(0, unit="DKK"),
        )


def test_invalid_economic_unit_rejected():
    with pytest.raises(ValueError, match="canonical unit"):
        AcquisitionOffer(
            "o",
            "v",
            AcquisitionMode.LEASE_NEW,
            term_months=obs(36, unit="month"),
            upfront_payment=obs(0, unit="EUR"),
        )


def test_cross_currency_eligible_ranking_rejected():
    c = Criterion("range", "range", PreferenceLabel.HIGH, anchors())
    profile = UserProfile("p", (c,), expected_annual_km=15000)
    vehicle = Vehicle("v", "M", "X", "A", {"range": obs(500)})
    dkk = evaluate_candidate(vehicle, lease_offer("dkk", "v", currency="DKK"), profile)
    eur = evaluate_candidate(vehicle, lease_offer("eur", "v", currency="EUR"), profile)
    with pytest.raises(ValueError, match="currencies"):
        rank_candidates([dkk, eur])


def test_deterministic_tie_uses_candidate_id_and_close_call_blocks_both():
    c = Criterion("range", "range", PreferenceLabel.HIGH, anchors())
    profile = UserProfile("p", (c,), expected_annual_km=15000)
    vehicle = Vehicle("v", "M", "X", "A", {"range": obs(500)})
    a = evaluate_candidate(vehicle, lease_offer("a", "v"), profile)
    b = evaluate_candidate(vehicle, lease_offer("b", "v"), profile)
    ranked = rank_candidates([b, a])
    assert ranked[0].candidate_id.endswith(":a")
    assert ranked[0].close_call is True
    assert ranked[1].close_call is True
    assert ranked[0].readiness == Readiness.NOT_READY
    assert ranked[1].readiness == Readiness.NOT_READY
