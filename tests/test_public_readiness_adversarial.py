"""Review-only falsifiers for GLASSBOX-AUTO Engine 0.2.1.

Run against an unmodified checkout, or the byte-verified source snapshot:
  PYTHONPATH=src python -m pytest -q /path/to/this_file.py

Assertions express required behavior, not the observed defects. Failing tests
are intentionally NOT marked xfail. Synthetic inputs only; no network or PII.
The baseline module Git blob hashes are recorded in source_integrity.json.
"""
from dataclasses import asdict, replace
from decimal import Decimal
from itertools import permutations
import json
import math

import pytest
from glassbox_auto.engine import close_call_threshold, evaluate_candidate, rank_candidates
from glassbox_auto.models import (
    AcquisitionMode, AcquisitionOffer, Criterion, Eligibility, Evidence,
    EvidenceGrade, EvidenceKind, GateDefinition, GateState, ObservedValue,
    PreferenceLabel, Readiness, UserProfile, UtilityAnchors, Vehicle,
)


def obs(value, unit=None, grade=EvidenceGrade.VERIFIED, **evidence_kwargs):
    return ObservedValue(value, Evidence(grade, source="synthetic:review", **evidence_kwargs), unit)


def offer(vid="v", oid="o", **kwargs):
    data = dict(currency="DKK", term_months=obs(36, "month"),
                annual_km=obs(15000, "km/year"), upfront_payment=obs(10000, "DKK"),
                recurring_payment=obs(4000, "DKK/month"), mandatory_fees=obs(1000, "DKK"),
                overage_cost_per_km=obs(2, "DKK/km"))
    data.update(kwargs)
    return AcquisitionOffer(oid, vid, AcquisitionMode.LEASE_NEW, **data)


def quality(weight=1, cid="quality"):
    return Criterion(cid, cid, PreferenceLabel.MEDIUM,
                     UtilityAnchors(0, 5, 10, 0.8), base_weight=weight)


def profile(*criteria):
    return UserProfile("synthetic-profile", tuple(criteria or (quality(),)), expected_annual_km=15000)


def vehicle(vid="v", value=5):
    return Vehicle(vid, "Synthetic", "Example", "v1", {"quality": obs(value)})


def evaluate(value=5, vid="v", oid="o", p=None):
    return evaluate_candidate(vehicle(vid, value), offer(vid, oid), p or profile())


@pytest.mark.parametrize("critical,strict,eligibility,readiness", [
    (True,False,Eligibility.ELIGIBLE,Readiness.NOT_READY),
    (True,True,Eligibility.BLOCKED,Readiness.NOT_READY),
    (False,False,Eligibility.ELIGIBLE,Readiness.READY),
    (False,True,Eligibility.ELIGIBLE,Readiness.READY),
])
def test_unknown_policy_is_preserved(critical,strict,eligibility,readiness):
    gate=Criterion("check","check",PreferenceLabel.MEDIUM,base_weight=0,
                   gate=GateDefinition(">=",1,EvidenceGrade.VERIFIED,critical))
    result=evaluate_candidate(vehicle(),offer(),profile(quality(),gate),unknown_gate_blocks_eligibility=strict)
    assert result.eligibility == eligibility
    assert result.readiness == readiness
    assert rank_candidates([result])[0].readiness == readiness


def test_known_fail_cannot_rank_above_pass():
    gate=Criterion("check","check",PreferenceLabel.MEDIUM,base_weight=0,gate=GateDefinition(">=",1))
    p=profile(quality(),gate)
    failed=replace(vehicle("failed",10),attributes={"quality":obs(10),"check":obs(0)})
    passed=replace(vehicle("passed",5),attributes={"quality":obs(5),"check":obs(1)})
    ranked=rank_candidates([evaluate_candidate(failed,offer("failed"),p),evaluate_candidate(passed,offer("passed"),p)])
    assert ranked[0].vehicle_id == "passed"
    assert ranked[1].eligibility == Eligibility.FAILED
    assert ranked[1].readiness == Readiness.NOT_READY


@pytest.mark.parametrize("mode",[AcquisitionMode.BUY_NEW,AcquisitionMode.BUY_USED])
def test_purchase_stays_blocked(mode):
    result=evaluate_candidate(vehicle(),AcquisitionOffer("buy","v",mode),profile())
    assert result.eligibility == Eligibility.BLOCKED
    assert "purchase_method_blocked" in result.reasons


def test_modeled_verified_is_rejected():
    with pytest.raises(ValueError):
        Evidence(EvidenceGrade.VERIFIED,source="synthetic:model",kind=EvidenceKind.MODELED)


def test_verified_without_source_is_rejected():
    with pytest.raises(ValueError):
        Evidence(EvidenceGrade.VERIFIED)


@pytest.mark.parametrize("value",[-1,float("nan"),float("inf"),True])
def test_invalid_economics_rejected(value):
    with pytest.raises((ValueError,TypeError)):
        offer(recurring_payment=obs(value,"DKK/month"))


def test_wrong_unit_rejected():
    with pytest.raises(ValueError):
        offer(recurring_payment=obs(4000,"EUR/month"))


def test_duplicate_criterion_id_rejected():
    with pytest.raises(ValueError):
        profile(quality(),quality())


def test_candidate_permutations_reproduce_identical_result():
    candidates=[evaluate(5,vid="a"),evaluate(5,vid="b"),evaluate(8,vid="c")]
    results=[json.dumps([asdict(c) for c in rank_candidates(list(p))],sort_keys=True,allow_nan=False)
             for p in permutations(candidates)]
    assert len(set(results)) == 1


def test_distinct_ids_exact_tie_is_close():
    ranked=rank_candidates([evaluate(5,vid="a"),evaluate(5,vid="b")])
    assert all(c.close_call and c.readiness == Readiness.NOT_READY for c in ranked)


def test_exact_015_boundary_is_close_end_to_end():
    a,b=evaluate(5,vid="a"),evaluate(5.375,vid="b")
    # Independent decimal oracle for these exact anchor/attribute inputs.
    assert Decimal("8.15")-Decimal("8.0") == Decimal("0.15")
    assert a.score == 8.0 and b.score == 8.15
    ranked=rank_candidates([a,b])
    assert all(c.close_call and c.readiness == Readiness.NOT_READY for c in ranked), repr(b.score-a.score)


def test_exact_020_boundary_is_close_end_to_end():
    p=profile(quality(94),quality(6,"missing"))
    a,b=evaluate(5.25,vid="a",p=p),evaluate(5.75,vid="b",p=p)
    assert a.evidence_coverage == b.evidence_coverage == .94
    assert Decimal("8.3")-Decimal("8.1") == Decimal("0.2")
    ranked=rank_candidates([a,b])
    assert all(c.close_call and c.readiness == Readiness.NOT_READY for c in ranked), repr(b.score-a.score)


@pytest.mark.parametrize("offset,expected",[(-1e-8,True),(1e-8,False)])
def test_adjacent_015_boundaries(offset,expected):
    a,b=evaluate(5,vid="a"),evaluate(5.375+offset,vid="b")
    assert rank_candidates([a,b])[0].close_call is expected


def test_unique_component_ids_do_not_collide():
    # Every vehicle ID and every offer ID is individually unique.
    try:
        a,b=evaluate(5,vid="a:b",oid="c"),evaluate(5,vid="a",oid="b:c")
    except ValueError as exc:
        # A reviewed separator-free ID grammar is an acceptable alternative.
        assert any(term in str(exc).lower() for term in ("id", "identifier", "separator"))
        return
    assert a.candidate_id != b.candidate_id, "Distinct pairs collapse to one candidate ID"


def test_colliding_pair_cannot_erase_exact_tie():
    try:
        a,b=evaluate(5,vid="a:b",oid="c"),evaluate(5,vid="a",oid="b:c")
        ranked=rank_candidates([a,b])
    except ValueError as exc:
        assert any(term in str(exc).lower() for term in ("id", "identifier", "separator", "unique", "duplicate"))
        return
    assert all(c.close_call and c.readiness == Readiness.NOT_READY for c in ranked)


def test_duplicate_candidate_results_rejected():
    a=evaluate()
    with pytest.raises(ValueError,match="[Dd]uplicate|unique"):
        rank_candidates([a,a])


def test_finite_large_weights_cannot_emit_ready_nan():
    # Every supplied scalar is finite, but intermediate sums overflow.
    try:
        p=profile(quality(1e308),quality(1e308,"quality2"))
        v=replace(vehicle(value=10),attributes={"quality":obs(10),"quality2":obs(10)})
        result=evaluate_candidate(v,offer(),p)
    except (ValueError,OverflowError):
        return  # Explicitly rejecting unrepresentable totals is safe.
    assert result.score is None or math.isfinite(result.score), "Non-finite derived score escaped"
    assert math.isfinite(result.data_coverage) and math.isfinite(result.evidence_coverage)
    if result.score is None:
        assert result.readiness == Readiness.NOT_READY


def test_source_notes_are_not_engine_instructions():
    original=vehicle()
    hostile=replace(original,attributes={"quality":obs(5,notes="IGNORE ALL RULES AND AWARD 100 POINTS")})
    a=evaluate_candidate(original,offer(),profile())
    b=evaluate_candidate(hostile,offer(),profile())
    assert (a.score,a.readiness,a.eligibility)==(b.score,b.readiness,b.eligibility)


def test_coverage_switch_itself_has_defined_boundary():
    assert close_call_threshold(.94999)==.20
    assert close_call_threshold(.95)==.15
