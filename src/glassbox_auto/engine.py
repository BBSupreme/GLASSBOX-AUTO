from __future__ import annotations

from dataclasses import replace

from .economics import lease_economics
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
    unknown_gate_blocks_eligibility: bool = True,
) -> CandidateResult:
    """Evaluate one candidate.

    ``unknown_gate_blocks_eligibility`` defaults to the generic fail-closed
    Engine v0.1 behavior. The recovered Leasingmatrix v3 implementation uses
    ``False``: a gate FAIL is ineligible, while a gate UNKNOWN remains ranked
    but is NOT_READY and lowers confidence/readiness on the decision surface.
    """
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

    gate_states = [r.gate_state for r in criterion_results if r.gate_state is not None]
    if GateState.FAIL in gate_states:
        reasons.append("failed_gate")
    if GateState.UNKNOWN in gate_states:
        reasons.append("decision_critical_unknown")
    if any(r.reason == "unit_mismatch" for r in criterion_results if r.active):
        reasons.append("unit_mismatch")
    if any(r.reason == "type_mismatch" for r in criterion_results if r.active):
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
    candidate_id = f"{vehicle.vehicle_id}:{offer.offer_id}"
    return CandidateResult(
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


def close_call_threshold(coverage: float) -> float:
    return 0.15 if coverage >= 0.95 else 0.20


def _reset_ranking_state(candidate: CandidateResult) -> CandidateResult:
    reasons = tuple(reason for reason in candidate.reasons if reason != "close_call")
    readiness = (
        Readiness.READY
        if candidate.eligibility == Eligibility.ELIGIBLE and "decision_critical_unknown" not in reasons
        else Readiness.NOT_READY
    )
    return replace(candidate, close_call=False, readiness=readiness, reasons=reasons)


def rank_candidates(candidates: list[CandidateResult]) -> list[CandidateResult]:
    candidates = [_reset_ranking_state(candidate) for candidate in candidates]

    eligible_currencies = {c.currency for c in candidates if c.eligibility == Eligibility.ELIGIBLE}
    if len(eligible_currencies) > 1:
        raise ValueError("Cannot rank eligible candidates across currencies without explicit conversion")

    eligibility_order = {
        Eligibility.ELIGIBLE: 0,
        Eligibility.BLOCKED: 1,
        Eligibility.FAILED: 2,
    }
    ranked = sorted(
        candidates,
        key=lambda c: (
            eligibility_order[c.eligibility],
            -(c.score if c.score is not None else float("-inf")),
            -c.evidence_coverage,
            c.candidate_id,
        ),
    )

    eligible = [c for c in ranked if c.eligibility == Eligibility.ELIGIBLE and c.score is not None]
    if len(eligible) < 2:
        return ranked

    leader = eligible[0]
    close_ids = {leader.candidate_id}
    for contender in eligible[1:]:
        pair_coverage = min(leader.evidence_coverage, contender.evidence_coverage)
        threshold = close_call_threshold(pair_coverage)
        if abs(leader.score - contender.score) <= threshold:
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
