from __future__ import annotations

from dataclasses import replace
import math

from .models import (
    Criterion,
    CriterionResult,
    GRADE_RANK,
    GateDefinition,
    GateState,
    ObservedValue,
    PREFERENCE_MULTIPLIERS,
    PreferenceLabel,
    UtilityAnchors,
    UtilityDirection,
)


def piecewise_utility(value: float, anchors: UtilityAnchors) -> float:
    f, n, s, u_need = anchors.floor, anchors.need, anchors.stretch, anchors.need_utility
    if anchors.direction == UtilityDirection.HIGHER_IS_BETTER:
        if not (f < n < s):
            raise ValueError("HIGHER_IS_BETTER requires floor < need < stretch")
        if value <= f:
            return 0.0
        if value < n:
            return u_need * (value - f) / (n - f)
        if value < s:
            return u_need + (1.0 - u_need) * (value - n) / (s - n)
        return 1.0
    if not (f > n > s):
        raise ValueError("LOWER_IS_BETTER requires floor > need > stretch")
    if value >= f:
        return 0.0
    if value > n:
        return u_need * (f - value) / (f - n)
    if value > s:
        return u_need + (1.0 - u_need) * (n - value) / (n - s)
    return 1.0


def _is_number(value) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _gate_type_matches(value, threshold) -> bool:
    if _is_number(threshold):
        return _is_number(value)
    if isinstance(threshold, bool):
        return isinstance(value, bool)
    return isinstance(value, type(threshold))


def _compare(value, operator: str, threshold) -> bool:
    ops = {
        ">=": lambda a, b: a >= b,
        ">": lambda a, b: a > b,
        "<=": lambda a, b: a <= b,
        "<": lambda a, b: a < b,
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
    }
    try:
        return ops[operator](value, threshold)
    except KeyError as exc:
        raise ValueError(f"Unsupported gate operator: {operator}") from exc


def evaluate_gate(observed: ObservedValue | None, gate: GateDefinition) -> GateState:
    if observed is None or observed.value is None:
        return GateState.UNKNOWN
    if GRADE_RANK[observed.evidence.grade] < GRADE_RANK[gate.minimum_evidence]:
        return GateState.UNKNOWN
    if not _gate_type_matches(observed.value, gate.threshold):
        return GateState.UNKNOWN
    try:
        return GateState.PASS if _compare(observed.value, gate.operator, gate.threshold) else GateState.FAIL
    except TypeError:
        return GateState.UNKNOWN


def _effective_weight(criterion: Criterion, dimension_weights: dict[str, float]) -> float:
    dimension_weight = dimension_weights.get(criterion.dimension, 1.0) if criterion.dimension else 1.0
    weight = criterion.base_weight * criterion.subweight * dimension_weight * PREFERENCE_MULTIPLIERS[criterion.preference]
    if criterion.weight_cap is not None:
        weight = min(weight, criterion.weight_cap)
    if criterion.preference == PreferenceLabel.MUST_HAVE and criterion.active and weight <= 0:
        raise ValueError(
            f"Must-have criterion {criterion.criterion_id} must retain a positive effective weight in addition to its gate"
        )
    return weight


def score_candidate(
    criteria: tuple[Criterion, ...],
    attributes: dict[str, ObservedValue],
    dimension_weights: dict[str, float] | None = None,
):
    dimension_weights = dimension_weights or {}
    total_active_weight = sum(_effective_weight(criterion, dimension_weights) for criterion in criteria if criterion.active)
    data_weight = 0.0
    sufficient_weight = 0.0
    scored_weight = 0.0
    weighted_utility = 0.0
    results: list[CriterionResult] = []

    for criterion in criteria:
        weight = _effective_weight(criterion, dimension_weights)
        if not criterion.active:
            results.append(CriterionResult(criterion.criterion_id, None, weight, None, False, False, False, False, reason="inactive"))
            continue

        observed = attributes.get(criterion.attribute)
        data_present = observed is not None and observed.value is not None
        unit_matches = bool(not data_present or criterion.unit is None or observed.unit == criterion.unit)
        anchor_type_matches = bool(
            not data_present
            or criterion.anchors is None
            or _is_number(observed.value)
        )
        gate_type_matches = bool(
            not data_present
            or criterion.gate is None
            or _gate_type_matches(observed.value, criterion.gate.threshold)
        )
        type_matches = anchor_type_matches and gate_type_matches
        evidence_sufficient = bool(
            data_present
            and unit_matches
            and type_matches
            and GRADE_RANK[observed.evidence.grade] >= GRADE_RANK[criterion.minimum_evidence]
        )
        if data_present:
            data_weight += weight
        if evidence_sufficient:
            sufficient_weight += weight

        if criterion.gate is None:
            gate_state = None
        elif not unit_matches or not type_matches:
            gate_state = GateState.UNKNOWN
        else:
            gate_state = evaluate_gate(observed, criterion.gate)

        if not data_present:
            results.append(CriterionResult(criterion.criterion_id, None, weight, gate_state, False, False, True, False, reason="missing"))
            continue
        if not unit_matches:
            results.append(CriterionResult(criterion.criterion_id, None, weight, gate_state, True, False, True, False, reason="unit_mismatch"))
            continue
        if not type_matches:
            results.append(CriterionResult(criterion.criterion_id, None, weight, gate_state, True, False, True, False, reason="type_mismatch"))
            continue
        if not evidence_sufficient:
            results.append(CriterionResult(criterion.criterion_id, None, weight, gate_state, True, False, True, False, reason="insufficient_evidence"))
            continue
        if criterion.anchors is None:
            results.append(CriterionResult(criterion.criterion_id, None, weight, gate_state, True, True, True, False, reason="gate_only"))
            continue

        utility = piecewise_utility(observed.value, criterion.anchors)
        scored_weight += weight
        weighted_utility += utility * weight
        results.append(CriterionResult(criterion.criterion_id, utility, weight, gate_state, True, True, True, True))

    score = None if scored_weight == 0 else 10.0 * weighted_utility / scored_weight
    data_coverage = 0.0 if total_active_weight == 0 else data_weight / total_active_weight
    evidence_coverage = 0.0 if total_active_weight == 0 else sufficient_weight / total_active_weight

    if scored_weight:
        results = [replace(result, normalized_weight=(result.weight / scored_weight if result.scorable else 0.0)) for result in results]

    return score, data_coverage, evidence_coverage, tuple(results)
