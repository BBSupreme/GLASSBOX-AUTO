from __future__ import annotations

from .models import (
    Criterion,
    CriterionResult,
    EvidenceGrade,
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
    f, n, s = anchors.floor, anchors.need, anchors.stretch
    if anchors.direction == UtilityDirection.HIGHER_IS_BETTER:
        if not (f < n < s):
            raise ValueError("HIGHER_IS_BETTER requires floor < need < stretch")
        if value <= f:
            return 0.0
        if value < n:
            return 0.8 * (value - f) / (n - f)
        if value < s:
            return 0.8 + 0.2 * (value - n) / (s - n)
        return 1.0
    if not (f > n > s):
        raise ValueError("LOWER_IS_BETTER requires floor > need > stretch")
    if value >= f:
        return 0.0
    if value > n:
        return 0.8 * (f - value) / (f - n)
    if value > s:
        return 0.8 + 0.2 * (n - value) / (n - s)
    return 1.0


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
    return GateState.PASS if _compare(observed.value, gate.operator, gate.threshold) else GateState.FAIL


def score_candidate(criteria: tuple[Criterion, ...], attributes: dict[str, ObservedValue]):
    active = [c for c in criteria if c.active]
    total_weight = sum(PREFERENCE_MULTIPLIERS[c.preference] for c in active)
    covered_weight = 0.0
    scored_weight = 0.0
    weighted_utility = 0.0
    results: list[CriterionResult] = []

    for criterion in active:
        weight = PREFERENCE_MULTIPLIERS[criterion.preference]
        observed = attributes.get(criterion.attribute)
        covered = bool(
            observed is not None
            and observed.value is not None
            and observed.evidence.grade != EvidenceGrade.UNKNOWN
        )
        if covered:
            covered_weight += weight

        gate_state = None
        if criterion.preference == PreferenceLabel.MUST_HAVE:
            if criterion.gate is None:
                raise ValueError(f"Must-have criterion {criterion.criterion_id} requires a gate")
            gate_state = evaluate_gate(observed, criterion.gate)
        elif criterion.gate is not None:
            gate_state = evaluate_gate(observed, criterion.gate)

        if observed is None or observed.value is None or criterion.anchors is None:
            results.append(CriterionResult(criterion.criterion_id, None, weight, gate_state, covered, "missing_or_unscorable"))
            continue
        if GRADE_RANK[observed.evidence.grade] < GRADE_RANK[criterion.minimum_evidence]:
            results.append(CriterionResult(criterion.criterion_id, None, weight, gate_state, covered, "insufficient_evidence"))
            continue

        utility = piecewise_utility(float(observed.value), criterion.anchors)
        scored_weight += weight
        weighted_utility += utility * weight
        results.append(CriterionResult(criterion.criterion_id, utility, weight, gate_state, covered))

    score = None if scored_weight == 0 else 10.0 * weighted_utility / scored_weight
    coverage = 0.0 if total_weight == 0 else covered_weight / total_weight
    return score, coverage, tuple(results)
