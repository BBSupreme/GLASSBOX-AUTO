from __future__ import annotations

from dataclasses import replace

from .economics import PurchaseMethodBlockedError, lease_economics
from .models import (
    AcquisitionMode,
    AcquisitionOffer,
    CandidateResult,
    GateState,
    Readiness,
    UserProfile,
    Vehicle,
)
from .scoring import score_candidate


def _merged_attributes(vehicle: Vehicle, offer: AcquisitionOffer):
    merged = dict(vehicle.attributes)
    merged.update(offer.attributes)
    return merged


def evaluate_candidate(vehicle: Vehicle, offer: AcquisitionOffer, profile: UserProfile) -> CandidateResult:
    if offer.vehicle_id != vehicle.vehicle_id:
        raise ValueError("Offer vehicle_id does not match vehicle")

    score, coverage, criterion_results = score_candidate(profile.criteria, _merged_attributes(vehicle, offer))
    reasons: list[str] = []

    gate_states = [r.gate_state for r in criterion_results if r.gate_state is not None]
    if GateState.FAIL in gate_states:
        reasons.append("failed_gate")
    if GateState.UNKNOWN in gate_states:
        reasons.append("decision_critical_unknown")
    if score is None:
        reasons.append("no_scorable_criteria")

    economics = None
    if offer.mode == AcquisitionMode.LEASE_NEW:
        economics = lease_economics(offer, profile)
    else:
        reasons.append("purchase_method_blocked")

    readiness = Readiness.READY if not reasons else Readiness.NOT_READY
    candidate_id = f"{vehicle.vehicle_id}:{offer.offer_id}"
    return CandidateResult(
        candidate_id=candidate_id,
        vehicle_id=vehicle.vehicle_id,
        offer_id=offer.offer_id,
        mode=offer.mode,
        score=score,
        evidence_coverage=coverage,
        readiness=readiness,
        criterion_results=criterion_results,
        economics=economics,
        reasons=tuple(reasons),
    )


def close_call_threshold(coverage: float) -> float:
    return 0.15 if coverage >= 0.95 else 0.20


def rank_candidates(candidates: list[CandidateResult]) -> list[CandidateResult]:
    def failed(c: CandidateResult) -> bool:
        return any(r.gate_state == GateState.FAIL for r in c.criterion_results)

    ranked = sorted(
        candidates,
        key=lambda c: (
            failed(c),
            -(c.score if c.score is not None else float("-inf")),
            -c.evidence_coverage,
            c.candidate_id,
        ),
    )

    if len(ranked) >= 2 and ranked[0].score is not None and ranked[1].score is not None:
        coverage = min(ranked[0].evidence_coverage, ranked[1].evidence_coverage)
        threshold = close_call_threshold(coverage)
        if abs(ranked[0].score - ranked[1].score) <= threshold:
            ranked[0] = replace(
                ranked[0],
                close_call=True,
                readiness=Readiness.NOT_READY,
                reasons=tuple(dict.fromkeys((*ranked[0].reasons, "close_call"))),
            )
            ranked[1] = replace(
                ranked[1],
                close_call=True,
                reasons=tuple(dict.fromkeys((*ranked[1].reasons, "close_call"))),
            )
    return ranked
