# GLASSBOX-AUTO Engine v0.1 — Implementation Specification

**Status:** implementation candidate under adversarial review  
**Date:** 2026-09-02  
**Scope:** headless decision engine for vehicle/acquisition comparison

## 1. Objective and compliance boundary

GLASSBOX-AUTO v0.1 is an implementation-independent, deterministic decision engine whose outputs can be audited from source evidence through to recommendation.

It implements the binding semantics documented in `DECISIONS.md` and `METHOD.md` where those semantics are known. It MUST NOT invent missing historical v3 profile values or unresolved purchase assumptions. Exact v3/v3.2.1 reproduction remains pending recovery of the original workbook, QA harness and economics anchors tracked in Issue #1.

Excel is a reference interface, not the source of truth.

## 2. Canonical entities

### Vehicle
Stable facts about a car/configuration. Vehicle facts MUST NOT contain offer-specific economics.

### AcquisitionOffer
A concrete acquisition offer linked to one Vehicle. Supported structural modes are `LEASE_NEW`, `BUY_NEW` and `BUY_USED`.

Decision-critical lease fields — term, annual km, upfront payment, recurring payment, mandatory fees and overage rate — are `ObservedValue`s carrying field-level evidence and canonical units.

### UserProfile
Contains explicit criteria, scenario inputs and weighting structure. A criterion can declare preference label, Floor / Need / Stretch anchors, explicit `need_utility`, gate, minimum evidence, dimension, base weight, subweight, optional cap and expected unit.

### DecisionCandidate
Derived comparison object containing criterion results, gates, score, data coverage, decision-sufficient evidence coverage, economics, eligibility, readiness, close-call state and reasons.

## 3. Evidence contract

Grades: `UNKNOWN | ESTIMATED | VERIFIED`.

Kinds: `DIRECT | DERIVED | MODELED`.

Rules:

1. VERIFIED evidence requires a source.
2. MODELED evidence cannot be VERIFIED.
3. Deterministic derived values inherit the weakest required input grade and retain source lineage.
4. A value materially dependent on a user scenario or forecast cannot be promoted above ESTIMATED merely because market inputs are VERIFIED.
5. Data presence and decision-sufficient evidence are separate measures.
6. Decision-sufficient evidence requires the criterion's minimum grade plus a satisfied type/unit contract.

## 4. Weighting

Binding label multipliers:

| Label | Multiplier | Gate |
|---|---:|---|
| LOW | 0.5 | No |
| MEDIUM | 1.0 | No |
| HIGH | 1.5 | No |
| VERY_HIGH | 2.0 | No |
| MUST_HAVE | 2.0 | Yes |

Effective weight:

`base_weight × subweight × dimension_weight × label_multiplier`, followed by an optional cap.

This supplies explicit primitives for dimension weights, editable subweights, the established baggage split and capped evidence structures without claiming that the unrecovered historical numeric profile has already been reconstructed.

Only active, scorable criteria enter the score denominator. Inactive/excluded criteria remain visible with zero normalized contribution. An active positive-weight criterion MUST have utility anchors; a deliberate gate-only criterion has `base_weight=0` plus an explicit gate.

## 5. Utility

Utility is piecewise-linear using explicit Floor / Need / Stretch anchors. `need_utility` is mandatory because the available binding documents do not establish one canonical numerical utility at Need.

For `HIGHER_IS_BETTER`, utility progresses `0 → need_utility → 1` across Floor → Need → Stretch and is capped outside the anchors. `LOWER_IS_BETTER` mirrors the curve.

No hidden anchor or silent numeric-string coercion is permitted.

## 6. Gates and eligibility

Gate states are `PASS | FAIL | UNKNOWN`. Missing values, insufficient evidence, incompatible units or incompatible numeric types make the gate UNKNOWN rather than FAIL or PASS.

A MUST_HAVE criterion MUST contain both an operational gate and a scoring definition, preserving Must-have = Very High weight + gate.

Candidate eligibility is independent of score:

- `ELIGIBLE`: no failed gate and no decision-critical blocker.
- `BLOCKED`: unresolved gate, incomplete economics, unit/type mismatch, purchase-method blocker, no score, or another decision-critical unknown.
- `FAILED`: at least one failed gate.

Only ELIGIBLE candidates can be promoted or participate in close-call formation.

## 7. Coverage

**Data coverage** is the active weight share with a present value.

**Evidence coverage** is the active weight share whose value is present, satisfies the criterion's type/unit contract and meets its minimum evidence grade.

The 95% close-call boundary uses evidence coverage, not mere data presence.

## 8. Lease economics

Base cash cost:

`upfront + recurring_payment × months + mandatory_fees`

Mileage fit compares expected annual km with contracted annual km over the term.

- If expected km exceeds contracted km and overage pricing is unavailable, overage cost and adjusted total are UNKNOWN/None.
- If expected km is below contracted km and no explicit unused-km value assumption exists, unused-km loss and adjusted total are UNKNOWN/None.
- An unused-km value assumption MUST use `<offer currency>/km`; a currency/unit mismatch is UNKNOWN and blocks readiness.
- Missing or UNKNOWN decision-critical lease evidence blocks readiness.

The economics layer emits provenance-bearing derived attributes including `economics.base_cash_cost` and `economics.total_adjusted_cost`. These enter the same criterion pipeline as other decision variables. Scenario-adjusted total cost is capped at ESTIMATED and retains lineage to the relevant offer evidence and `user_profile.expected_annual_km`.

## 9. Entity separation

Vehicle, offer and derived attribute domains may not silently overwrite one another. Key collisions are rejected.

## 10. Units and currency

Canonical lease units:

- term: `month`
- annual mileage: `km/year`
- upfront payment and mandatory fees: offer currency
- recurring payment: `<currency>/month`
- overage rate: `<currency>/km`

A criterion may declare an expected unit. Mismatches are non-scorable, not evidence-sufficient, and block readiness. Eligible candidates in different currencies cannot be ranked together without an explicit conversion layer.

## 11. Ranking and close calls

Deterministic display order:

1. ELIGIBLE
2. BLOCKED
3. FAILED
4. score descending
5. evidence coverage descending
6. `candidate_id` ascending

The internal score remains 0–10 for compatibility with historical falsification bands:

- gap ≤ 0.20 when pairwise evidence coverage <95%
- gap ≤ 0.15 when pairwise evidence coverage ≥95%

Pairwise coverage is the conservative minimum of leader and contender evidence coverage. The leader is tested against **all eligible contenders**. Every eligible contender within the band is marked close-call and NOT_READY at recommendation level. Ranking recomputes close-call state on every invocation to prevent stale state.

## 12. Purchase economics

`BUY_NEW` and `BUY_USED` remain method-blocked. Do not implement decision-ready purchase economics until the original P1–P3 findings and economics anchors are recovered, residual scenarios and break-even residual logic are validated, and financing cash-flow/economic-cost reconciliation tests exist.

Loan principal remains separate from economic cost.

## 13. Validation and QA

The regression suite must falsify, at minimum:

- multiplier mapping;
- explicit Need utility;
- missing-data denominator behavior;
- data vs decision-sufficient evidence coverage;
- inactive/excluded weight visibility;
- dimensions/subweights/caps;
- prevention of positive-weight dead criteria;
- gate PASS/FAIL/UNKNOWN;
- MUST_HAVE cannot become gate-only;
- MODELED cannot be VERIFIED;
- scenario-adjusted economics cannot self-promote to VERIFIED and retains lineage;
- 94.9%/95.0% close-call boundary;
- UNKNOWN-gate and purchase-blocked candidates cannot outrank eligible candidates;
- failed/blocked candidates cannot create close calls;
- 3+ eligible contenders inside the band;
- close-call ranking is idempotent;
- economics can change ranking when explicitly configured as a criterion;
- missing overage and unused-km pricing remain UNKNOWN, not zero;
- UNKNOWN economic evidence blocks readiness;
- unused-km assumption currency/unit mismatch blocks readiness;
- vehicle/offer collision rejection;
- negative economics rejection;
- canonical economic unit validation;
- criterion unit mismatch rejection;
- numeric-string/type mismatch rejection;
- cross-currency eligible ranking rejection;
- deterministic final tie ordering.

Excel/LibreOffice compatibility remains a release condition for the workbook frontend, not for this headless engine package.

## 14. Non-goals

v0.1 does not include live scraping, source-freshness verification, unresolved purchase assumptions, UI/Excel generation, probabilistic residual forecasting, automatic source verification, or reconstruction of missing v3 anchors from memory.

## 15. Release condition

Engine v0.1 may merge only when:

1. CI is green on the current PR head;
2. adversarial review is rerun on that same head;
3. no unresolved P0 remains;
4. remaining P1/P2 limitations are explicit and do not silently weaken a binding decision.
