from __future__ import annotations

from dataclasses import replace

from .economics import lease_economics
from .integrity import (is_close_call, make_candidate_id, require_finite_tree, require_identifier, require_range)
from .models import (
    AcquisitionMode,
    AcquisitionOffer,
    CandidateResult,
    Eligibility,
    GateState,
    Readiness,
    UserProfile,
    Vehicle,
)
from .scoring import score_candidate


def _merged_attributes(vehicle: Vehicle, offer: AcquisitionOffer, derived: dict):
    collisions = set(vehicle.attributes) & set(offer.attributes)
    if collisions:
        keys = ", ".join(sorted(collisions))
        raise ValueError(f"Vehicle/offer attribute collision: {keys}")

    merged = dict(vehicle.attributes)
    merged.update(offer.attributes)

    derived_collisions = set(derived) & set(merged)
    if derived_collisions:
        keys = ", ".join(sorted(derived_collisions))
        raise ValueError(f"Derived attribute collision: {keys}")

    merged.update(derived)
    return merged


def evaluate_candidate(
    vehicle: Vehicle,
    offer: AcquisitionOffer,
    profile: UserProfile,
    *,
    unknown_gate_blocks_eligibility: bool = False,
) -> CandidateResult:
    """Evaluate one candidate.

    ``unknown_gate_blocks_eligibility`` controls only *decision-critical* gate
    unknowns. Non-critical UNKNOWN gates reduce evidence coverage but do not
    affect eligibility or readiness.

    Engine 0.2.1 defaults to the binding Revision A D-V3.25 boundary:
    decision-critical UNKNOWN may remain rank-eligible but is always NOT_READY.
    Callers that require a stricter fail-closed ranking policy can explicitly
    pass ``unknown_gate_blocks_eligibility=True``. Gate FAIL remains ineligible
    under both policies.
    """
    candidate_id = make_candidate_id(vehicle.vehicle_id, offer.offer_id)
    require_identifier(offer.vehicle_id, "offer.vehicle_id")
    if offer.vehicle_id != vehicle.vehicle_id:
        raise ValueError("Offer vehicle_id does not match vehicle")

    reasons: list[str] = []
    economics = None
    derived_attributes = {}

    if offer.mode == AcquisitionMode.LEASE_NEW:
        economics = lease_economics(offer, profile)
        derived_attributes = economics["derived_attributes"]
        if not economics["complete"]:
            reasons.extend(economics["reasons"])
    else:
        reasons.append("purchase_method_blocked")

    attributes = _merged_attributes(vehicle, offer, derived_attributes)
    score, data_coverage, evidence_coverage, criterion_results = score_candidate(
        profile.criteria,
        attributes,
        profile.dimension_weights,
    )

    criteria_by_id = {criterion.criterion_id: criterion for criterion in profile.criteria}
    gate_states = [result.gate_state for result in criterion_results if result.gate_state is not None]
    decision_critical_unknown = any(
        result.gate_state == GateState.UNKNOWN
        and criteria_by_id[result.criterion_id].gate is not None
        and criteria_by_id[result.criterion_id].gate.decision_critical
        for result in criterion_results
    )

    if GateState.FAIL in gate_states:
        reasons.append("failed_gate")
    if decision_critical_unknown:
        reasons.append("decision_critical_unknown")
    if any(result.reason == "unit_mismatch" for result in criterion_results if result.active):
        reasons.append("unit_mismatch")
    if any(result.reason == "type_mismatch" for result in criterion_results if result.active):
        reasons.append("type_mismatch")
    if score is None:
        reasons.append("no_scorable_criteria")

    if GateState.FAIL in gate_states:
        eligibility = Eligibility.FAILED
    else:
        eligibility_blockers = list(reasons)
        if not unknown_gate_blocks_eligibility:
            eligibility_blockers = [reason for reason in eligibility_blockers if reason != "decision_critical_unknown"]
        eligibility = Eligibility.BLOCKED if eligibility_blockers else Eligibility.ELIGIBLE

    readiness = (
        Readiness.READY
        if eligibility == Eligibility.ELIGIBLE and "decision_critical_unknown" not in reasons
        else Readiness.NOT_READY
    )
    result = CandidateResult(
        candidate_id=candidate_id,
        vehicle_id=vehicle.vehicle_id,
        offer_id=offer.offer_id,
        mode=offer.mode,
        currency=offer.currency,
        score=score,
        data_coverage=data_coverage,
        evidence_coverage=evidence_coverage,
        readiness=readiness,
        eligibility=eligibility,
        criterion_results=criterion_results,
        economics=economics,
        reasons=tuple(dict.fromkeys(reasons)),
    )
    _validate_candidate_result(result)
    return result


def close_call_threshold(coverage: float) -> float:
    require_range(coverage, 0.0, 1.0, "coverage")
    return 0.15 if coverage >= 0.95 else 0.20


def _reset_ranking_state(candidate: CandidateResult) -> CandidateResult:
    reasons = tuple(reason for reason in candidate.reasons if reason != "close_call")
    readiness = (
        Readiness.READY
        if candidate.eligibility == Eligibility.ELIGIBLE and "decision_critical_unknown" not in reasons
        else Readiness.NOT_READY
    )
    return replace(candidate, close_call=False, readiness=readiness, reasons=reasons)


def _validate_candidate_result(candidate: CandidateResult) -> None:
    for field in ("candidate_id", "vehicle_id", "offer_id"):
        require_identifier(getattr(candidate, field), field)
    require_finite_tree(candidate, "candidate")
    if candidate.score is not None:
        require_range(candidate.score, 0.0, 10.0, "score")
    elif candidate.eligibility == Eligibility.ELIGIBLE:
        raise ValueError("An eligible candidate must have a finite score")
    require_range(candidate.data_coverage, 0.0, 1.0, "data_coverage")
    require_range(candidate.evidence_coverage, 0.0, 1.0, "evidence_coverage")


def rank_candidates(candidates: list[CandidateResult]) -> list[CandidateResult]:
    seen_ids: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    for candidate in candidates:
        _validate_candidate_result(candidate)
        pair = (candidate.vehicle_id, candidate.offer_id)
        if candidate.candidate_id in seen_ids or pair in seen_pairs:
            raise ValueError("Duplicate candidate identity; IDs and vehicle/offer pairs must be unique")
        seen_ids.add(candidate.candidate_id)
        seen_pairs.add(pair)
    candidates = [_reset_ranking_state(candidate) for candidate in candidates]

    eligible_currencies = {candidate.currency for candidate in candidates if candidate.eligibility == Eligibility.ELIGIBLE}
    if len(eligible_currencies) > 1:
        raise ValueError("Cannot rank eligible candidates across currencies without explicit conversion")

    eligibility_order = {
        Eligibility.ELIGIBLE: 0,
        Eligibility.BLOCKED: 1,
        Eligibility.FAILED: 2,
    }
    ranked = sorted(
        candidates,
        key=lambda candidate: (
            eligibility_order[candidate.eligibility],
            -(candidate.score if candidate.score is not None else float("-inf")),
            -candidate.evidence_coverage,
            candidate.candidate_id,
        ),
    )

    eligible = [candidate for candidate in ranked if candidate.eligibility == Eligibility.ELIGIBLE and candidate.score is not None]
    if len(eligible) < 2:
        return ranked

    leader = eligible[0]
    close_ids = {leader.candidate_id}
    for contender in eligible[1:]:
        pair_coverage = min(leader.evidence_coverage, contender.evidence_coverage)
        threshold = close_call_threshold(pair_coverage)
        if is_close_call(leader.score, contender.score, threshold):
            close_ids.add(contender.candidate_id)

    if len(close_ids) == 1:
        return ranked

    patched: list[CandidateResult] = []
    for candidate in ranked:
        if candidate.candidate_id in close_ids:
            patched.append(
                replace(
                    candidate,
                    close_call=True,
                    readiness=Readiness.NOT_READY,
                    reasons=tuple(dict.fromkeys((*candidate.reasons, "close_call"))),
                )
            )
        else:
            patched.append(candidate)
    return patched
