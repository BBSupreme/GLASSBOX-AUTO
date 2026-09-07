"""Permanent adversarial controls for issues #11, #12 and #13 (synthetic only)."""
from dataclasses import asdict, replace
from itertools import permutations, product
import json
import math
import random

import pytest

from glassbox_auto.economics import lease_economics
from glassbox_auto.engine import close_call_threshold, evaluate_candidate, rank_candidates
from glassbox_auto.integrity import NumericalIntegrityError, is_close_call, make_candidate_id
from glassbox_auto.models import Eligibility, ObservedValue, Readiness, UtilityAnchors
from glassbox_auto.scoring import piecewise_utility, score_candidate
from test_public_readiness_adversarial import evaluate, obs, offer, profile, quality, vehicle


@pytest.mark.parametrize("threshold", [.15, .20])
@pytest.mark.parametrize("leader", [1.0, 5.0, 8.15, 9.75, 10.0])
@pytest.mark.parametrize("offset,expected", [(-1e-8, True), (0.0, True), (1e-8, False)])
def test_inclusive_score_boundary_at_multiple_magnitudes(threshold, leader, offset, expected):
    a = replace(evaluate(vid="a"), score=leader)
    b = replace(evaluate(vid="b"), score=leader - threshold - offset)
    if threshold == .20:
        a = replace(a, evidence_coverage=.94)
        b = replace(b, evidence_coverage=.94)
    result = rank_candidates([a, b])
    assert all(c.close_call == expected for c in result)
    assert all((c.readiness == Readiness.NOT_READY) == expected for c in result)


def test_tolerance_is_not_display_rounding_or_relative_default():
    assert is_close_call(8.15, 8.0, .15)
    assert is_close_call(8.15 + 2e-13, 8.0, .15)
    assert not is_close_call(8.15 + 1e-10, 8.0, .15)
    assert not is_close_call(8.151, 8.0, .15)


def test_coverage_switch_keeps_its_existing_exact_policy():
    assert close_call_threshold(math.nextafter(.95, 0.0)) == .20
    assert close_call_threshold(.95) == .15
    assert close_call_threshold(math.nextafter(.95, 1.0)) == .15


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf, -.01, 1.01, True])
def test_invalid_coverage_rejected(bad):
    with pytest.raises(ValueError):
        close_call_threshold(bad)


def test_component_encoding_is_injective_over_adversarial_corpus():
    components = ["a", "a:b", "%", "%3A", "a/b", "a b", "æ", "~", "_", "a%25b"]
    pairs = list(product(components, repeat=2))
    assert len({make_candidate_id(*pair) for pair in pairs}) == len(pairs)
    assert make_candidate_id("ordinary-id_1", "offer.2") == "ordinary-id_1:offer.2"
    assert make_candidate_id("a:b", "c") == "a%3Ab:c"
    assert make_candidate_id("a", "b:c") == "a:b%3Ac"
    assert make_candidate_id("a%3Ab", "c") != make_candidate_id("a:b", "c")


@pytest.mark.parametrize("bad", ["", " ", "a\x00b", "a\nb", "a\x7fb", None, 42, "\ud800"])
def test_invalid_component_ids_rejected(bad):
    with pytest.raises(ValueError, match="identifier|id"):
        evaluate(vid=bad)
    with pytest.raises(ValueError, match="identifier|id"):
        evaluate(oid=bad)


def test_duplicate_ids_and_duplicate_pairs_fail_separately():
    a, b = evaluate(vid="a"), evaluate(vid="b")
    with pytest.raises(ValueError, match="Duplicate"):
        rank_candidates([a, replace(b, candidate_id=a.candidate_id)])
    with pytest.raises(ValueError, match="Duplicate"):
        rank_candidates([a, replace(a, candidate_id="different")])


def test_encoded_ties_permute_and_rerank_without_readiness_loss():
    cases = [evaluate(vid="a:b", oid="c"), evaluate(vid="a", oid="b:c"), evaluate(vid="x")]
    outputs = []
    for order in permutations(cases):
        ranked = rank_candidates(list(order))
        assert all(c.close_call and c.readiness == Readiness.NOT_READY for c in ranked)
        assert ranked == rank_candidates(ranked)
        outputs.append(json.dumps([asdict(c) for c in ranked], sort_keys=True, allow_nan=False))
    assert len(set(outputs)) == 1


@pytest.mark.parametrize("field,bad", [("score", math.nan), ("score", math.inf), ("score", 11),
                                    ("score", True), ("data_coverage", math.inf),
                                    ("evidence_coverage", -.1), ("score", None)])
def test_rank_rejects_invalid_external_result(field, bad):
    with pytest.raises(ValueError):
        rank_candidates([replace(evaluate(), **{field: bad})])


def test_rank_rejects_nonfinite_criterion_and_economics_leaves():
    a = evaluate()
    with pytest.raises(ValueError):
        rank_candidates([replace(a, criterion_results=(replace(a.criterion_results[0], weight=math.inf),))])
    with pytest.raises(ValueError):
        rank_candidates([replace(a, economics={"hidden": {"amount": math.nan}})])


@pytest.mark.parametrize("case", ["sum", "product", "cap"])
def test_unrepresentable_weights_are_explicit_errors(case):
    c = quality(1e308)
    criteria = (c, quality(1e308, "quality2")) if case == "sum" else (c,)
    if case in {"product", "cap"}:
        criteria = (replace(c, subweight=2.0, weight_cap=1.0 if case == "cap" else None),)
    with pytest.raises(NumericalIntegrityError):
        score_candidate(criteria, {"quality": obs(10), "quality2": obs(10)})


@pytest.mark.parametrize("weight", [1e306, 1e308])
def test_large_but_representable_weight_not_arbitrarily_rejected(weight):
    score, coverage, evidence, results = score_candidate((quality(weight),), {"quality": obs(10)})
    assert (score, coverage, evidence) == (10.0, 1.0, 1.0)
    assert results[0].normalized_weight == 1.0


@pytest.mark.parametrize("kwargs,p", [
    ({"recurring_payment": obs(1e308, "DKK/month")}, profile()),
    ({"annual_km": obs(1e308, "km/year")}, profile()),
    ({}, replace(profile(), expected_annual_km=1e308)),
    ({"overage_cost_per_km": obs(1e308, "DKK/km")}, replace(profile(), expected_annual_km=20000)),
    ({}, replace(profile(), expected_annual_km=10000, unused_km_value_per_km=obs(1e308, "DKK/km"))),
])
def test_economics_intermediate_overflow_is_rejected(kwargs, p):
    with pytest.raises(NumericalIntegrityError):
        lease_economics(offer(**kwargs), p)


def test_mileage_nan_cannot_be_mistaken_for_zero_adjustment():
    o = offer(term_months=obs(1e308, "month"), recurring_payment=obs(0, "DKK/month"),
              annual_km=obs(1e308, "km/year"))
    p = replace(profile(), expected_annual_km=1e308)
    with pytest.raises(NumericalIntegrityError):
        lease_economics(o, p)


def test_unrepresentable_utility_span_cannot_silently_score_zero():
    with pytest.raises(NumericalIntegrityError):
        piecewise_utility(0, UtilityAnchors(-1e308, 1e308, 1.5e308, .8))


@pytest.mark.parametrize("n", [math.nan, math.inf, -math.inf, True])
def test_standalone_utility_rejects_nonfinite_values(n):
    with pytest.raises(ValueError):
        piecewise_utility(n, UtilityAnchors(0, 5, 10, .8))


def test_normal_mileage_costs_and_no_candidate_case_are_preserved():
    p = replace(profile(), expected_annual_km=20000)
    e = lease_economics(offer(), p)
    assert e["base_cash_cost"] == 155000
    assert e["overage_cost"] == 30000
    assert e["total_adjusted_cost"] == 185000
    assert rank_candidates([]) == []


@pytest.mark.parametrize("seed", list(range(20)))
@pytest.mark.parametrize("value,expected", [(0, 0.0), (5, 8.0), (10, 10.0)])
def test_ordinary_decimal_weights_have_consistent_coverage_and_bounded_score(seed, value, expected):
    rng = random.Random(seed)
    weights = [rng.uniform(.01, 100) for _ in range(rng.randint(1, 30))]
    criteria = tuple(quality(w, f"q{i}") for i, w in enumerate(weights))
    attrs = {f"q{i}": obs(value) for i in range(len(weights))}
    score, data, evidence, _ = score_candidate(criteria, attrs)
    assert (data, evidence) == (1.0, 1.0)
    assert score == pytest.approx(expected, abs=1e-12)
    assert 0.0 <= score <= 10.0


def test_python313_compensated_total_vs_sequential_subtotal_reproducer():
    weights = [89.24441007141745, 8.364232176300055, 59.20680241630467,
               42.380503349413786, 53.01350013169946, 13.038991095335579,
               19.207795782353877, 44.462911651562564, 22.11170692399034,
               45.50874555518316]
    criteria = tuple(quality(w, str(i)) for i, w in enumerate(weights))
    attrs = {str(i): obs(10) for i in range(len(weights))}
    score, data, evidence, _ = score_candidate(criteria, attrs)
    assert (score, data, evidence) == (10.0, 1.0, 1.0)
