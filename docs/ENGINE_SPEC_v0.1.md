# GLASSBOX-AUTO Engine v0.1 — Implementation Specification

**Status:** implementation candidate  
**Date:** 2026-09-02  
**Scope:** canonical decision engine for vehicle/acquisition comparison

## 1. Objective

Build an implementation-independent, deterministic decision engine whose outputs can be audited from source evidence through to recommendation.

The engine MUST preserve the binding v3 Revision A semantics documented in `DECISIONS.md` and `METHOD.md`. Excel is a reference interface, not the source of truth.

## 2. Canonical entities

### Vehicle
Stable facts about a car/configuration. A vehicle MUST NOT contain offer-specific economics.

Required identity fields:
- `vehicle_id`
- `make`
- `model`
- `variant`

Optional fact fields are stored in `attributes`, each as an `ObservedValue` with evidence metadata.

### AcquisitionOffer
A concrete way to acquire a vehicle.

Required fields:
- `offer_id`
- `vehicle_id`
- `mode`: `LEASE_NEW | BUY_NEW | BUY_USED`
- `currency`

Lease fields include term, annual contracted km, upfront payment, recurring payment, mandatory fees and optional overage assumptions.

Purchase fields may be represented structurally in v0.1, but decision-ready purchase economics are BLOCKED until the original P1–P3 findings and economics anchors are recovered.

### UserProfile
Contains explicit criteria and scenario inputs.

Each criterion declares:
- `criterion_id`
- `attribute`
- preference label
- utility anchors/direction
- optional must-have gate
- minimum evidence requirement

### DecisionCandidate
A derived comparison object linking one Vehicle, one AcquisitionOffer and one UserProfile evaluation.

It contains:
- gate results
- criterion results
- weighted score
- evidence-weight coverage
- excluded/inert criteria
- readiness state
- economics output

### Evidence
Every observed input can carry:
- `grade`: `UNKNOWN | ESTIMATED | VERIFIED`
- `source`
- `as_of`
- `notes`

Model-derived values MUST NOT self-promote to VERIFIED.

## 3. Preference multipliers

Binding mapping:

| label | multiplier | gate |
|---|---:|---|
| LOW | 0.5 | no |
| MEDIUM | 1.0 | no |
| HIGH | 1.5 | no |
| VERY_HIGH | 2.0 | no |
| MUST_HAVE | 2.0 | yes |

Weights are normalized over active criteria that have scorable data.

Missing data:
- MUST NOT become a zero utility;
- MUST be excluded from the scored denominator;
- MUST reduce evidence-weight coverage;
- MAY make the result not ready where decision-critical.

## 4. Utility

v0.1 supports deterministic piecewise-linear utility using explicit `floor`, `need`, and `stretch` anchors.

For `HIGHER_IS_BETTER`:
- value <= floor => 0
- floor..need => linear 0..0.8
- need..stretch => linear 0.8..1.0
- value >= stretch => 1.0

For `LOWER_IS_BETTER`, the curve is mirrored.

Anchors MUST satisfy the direction-specific ordering rules. No hidden anchors are allowed.

## 5. Gates

A must-have criterion is both weighted at 2.0 and evaluated as a decision-critical gate.

Gate states:
- `PASS`
- `FAIL`
- `UNKNOWN`

A gate operational definition MUST specify:
- attribute
- operator
- threshold/expected value
- minimum evidence grade

Missing values or insufficient evidence return UNKNOWN, not FAIL.

Any FAIL makes the candidate `NOT_READY`. Any decision-critical UNKNOWN makes the candidate `NOT_READY`.

## 6. Evidence-weight coverage

Coverage is calculated over all active criterion base weights:

`covered_weight / total_active_weight`

A criterion is covered when a value exists and its evidence grade is not UNKNOWN.

This metric is separate from the normalized score denominator.

## 7. Ranking and close calls

Candidates are ordered deterministically by:
1. gate eligibility (`FAIL` last)
2. score descending
3. evidence coverage descending
4. `candidate_id` ascending

Close-call threshold:
- `0.20` score points when evidence-weight coverage < 95%
- `0.15` score points when coverage >= 95%

The engine stores score internally on a 0–10 scale so the historical v3 thresholds remain directly interpretable.

A top-two difference within the applicable threshold is a close call and blocks `READY` status for the recommendation surface.

## 8. Lease economics

v0.1 implements transparent lease cash economics:

`base_cash_cost = upfront + recurring_payment * months + mandatory_fees`

Mileage adjustment supports:
- expected km above contracted km, if `overage_cost_per_km` is provided;
- expected km below contracted km as explicit `unused_km_value_loss`, using a caller-supplied value-per-unused-km assumption.

No default monetary value for unused km is invented by the engine.

Outputs expose every component.

## 9. Purchase economics

Architecture is present but production evaluation is deliberately blocked.

The engine MUST raise `PurchaseMethodBlockedError` for `BUY_NEW` and `BUY_USED` economics until:
1. original P1–P3 findings are imported and resolved;
2. economics Floor/Need/Stretch anchors are imported;
3. residual scenarios and break-even residual logic are validated;
4. financing cash-flow and economic-cost reconciliation tests exist.

This prevents accidental implementation-by-assumption.

## 10. Readiness

Candidate readiness values:
- `READY`
- `NOT_READY`

`NOT_READY` if any of the following apply:
- failed gate;
- decision-critical unknown gate;
- no scorable criteria;
- purchase mode is method-blocked.

Ranking-level readiness additionally becomes not-ready for a close call.

Completeness alone is not a readiness condition.

## 11. API surface

Primary package: `glassbox_auto`

Public functions/classes:
- schemas from `models.py`
- `piecewise_utility()`
- `evaluate_gate()`
- `score_candidate()`
- `lease_economics()`
- `evaluate_candidate()`
- `rank_candidates()`

No frontend-specific logic is permitted in the package.

## 12. QA acceptance criteria

v0.1 CI MUST verify:
- label multiplier mapping;
- missing-data denominator behavior;
- evidence coverage behavior;
- utility anchor boundaries;
- gate pass/fail/unknown/evidence behavior;
- deterministic tie ordering;
- 94.9% / 95.0% close-call boundary;
- lease cash-cost reconciliation;
- overage calculation;
- unused-km value-loss calculation only when supplied;
- purchase economics fail closed.

Excel/LibreOffice compatibility remains a release requirement for the workbook frontend, not for this headless engine package.

## 13. Non-goals for v0.1

- scraping live offers;
- defining unresolved purchase assumptions;
- UI/Excel generation;
- automatic evidence promotion;
- probabilistic residual-value forecasting;
- hiding uncertainty behind one composite confidence score.

## 14. Release condition

Engine v0.1 may merge when CI passes and review confirms that no code path silently weakens a binding decision documented in `docs/DECISIONS.md`.
