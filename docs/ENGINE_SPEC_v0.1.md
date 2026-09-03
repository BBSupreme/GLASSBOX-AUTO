# GLASSBOX-AUTO Engine v0.1 — Implementation Specification

**Status:** implementation candidate under adversarial review after source recovery  
**Date:** 2026-09-03  
**Scope:** headless decision engine for vehicle/acquisition comparison

## 1. Objective and compliance boundary

GLASSBOX-AUTO v0.1 is an implementation-independent, deterministic decision engine whose outputs can be audited from source evidence through to recommendation.

A substantial original Leasingmatrix package has now been recovered: Revision A, implementation handover, v2.1, a later v3 workbook whose Change_Log reaches v3.2, and earlier build/QA scripts. Exact v3.2.1 parity and the purchase-layer method remain pending the still-missing later fixture/source artifacts. See `RECOVERED_V3_ARTIFACTS_2026-09-03.md`.

Excel is a reference implementation and evidence fixture, not the headless source of truth.

## 2. Canonical entities

### Vehicle
Stable facts about a car/configuration. Vehicle facts MUST NOT contain offer-specific economics.

### AcquisitionOffer
A concrete acquisition offer linked to one Vehicle. Supported structural modes are `LEASE_NEW`, `BUY_NEW` and `BUY_USED`.

Decision-critical lease fields — term, annual km, upfront payment, recurring payment, mandatory fees and overage rate — are `ObservedValue`s carrying field-level evidence and canonical units.

### UserProfile
Contains explicit criteria, scenario inputs and weighting structure. A criterion can declare preference label, Floor / Need / Stretch anchors, `need_utility`, gate, minimum evidence, dimension, base weight, subweight, optional cap and expected unit.

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
7. Modeled real-world range is ESTIMATED; VERIFIED requires generation/variant-matched measurement evidence.

## 4. Weighting

Binding Revision A label multipliers:

| Label | Multiplier | Gate |
|---|---:|---|
| LOW | 0.5 | No |
| MEDIUM | 1.0 | No |
| HIGH | 1.5 | No |
| VERY_HIGH | 2.0 | No |
| MUST_HAVE | 2.0 | Yes |

Recovered default v3 base dimensions:

| Dimension | Base weight |
|---|---:|
| Economics | 35 |
| Practical / Family | 25 |
| Comfort & Driving | 15 |
| EV Usability | 15 |
| Equipment & UX | 10 |

Effective weight is profile-defined using explicit base/dimension/subweight primitives plus the label multiplier and optional cap. Weights normalize over active/scorable criteria.

A MUST_HAVE is not a separate weight level: it receives the Very High multiplier and spawns an operational gate.

Only active, scorable criteria enter the score denominator. Inactive/excluded criteria remain visible with zero normalized contribution. A deliberate gate-only criterion has `base_weight=0` plus an explicit gate.

## 5. Utility

Utility is piecewise-linear using explicit Floor / Need / Stretch anchors.

The recovered exact Revision A establishes canonical v3 utility values:

- Floor → 0/10
- Need → 8/10
- Stretch → 10/10

Therefore a v3 compatibility profile MUST use `need_utility=0.8`. The engine retains `need_utility` as an explicit field so other profiles cannot hide a different curve behind the same terminology.

Recovered v3 defaults include:

- real range: F=200, N=350, S=500 km;
- baggage: F=300, N=profile requirement (default 500), S=600 L;
- DC 10–80: F=45, N=28, S=18 minutes, lower is better;
- child protection inside Family: 70%→0 and 95%→10.

No hidden anchor or silent numeric-string coercion is permitted.

## 6. Gates, eligibility and readiness

Gate states are `PASS | FAIL | UNKNOWN`. Missing values, insufficient evidence, incompatible units or incompatible numeric types make the gate UNKNOWN rather than FAIL or PASS.

A MUST_HAVE criterion contains both an operational gate and a scoring definition, preserving Must-have = Very High weight + gate.

Recovered historical v3 semantics distinguish ranking eligibility from readiness:

- gate `FAIL` → ineligible/failed;
- decision-critical gate `UNKNOWN` may remain rank-eligible, but is NOT_READY;
- non-critical unknowns reduce evidence/confidence rather than automatically removing ranking eligibility.

Engine v0.1 exposes this historical policy through `evaluate_candidate(..., unknown_gate_blocks_eligibility=False)`. The generic engine default remains stricter (`True`) for profiles that deliberately want fail-closed ranking eligibility.

Other blockers such as incomplete decision-critical economics, unit/type mismatch, purchase-method blocking, or no score remain `BLOCKED`.

Only rank-eligible candidates can be promoted or participate in close-call formation.

Recovered v3 NCAP gate parameters are at least 5 stars and protocol year at least 2020. Exact generation-match evidence remains an ingestion/evidence responsibility.

## 7. Coverage

The engine exposes:

**Data coverage** — active weight share with a present value.

**Evidence coverage** — active weight share whose value is present, satisfies type/unit contracts and meets minimum evidence grade.

Exact Revision A D-V3.23 says the 95% close-call switch uses weight coverage. The recovered v3/v3.2 workbook instead uses a four-item critical-evidence count. Engine v0.1 currently follows the binding Revision A weight-coverage semantics. This spec/implementation divergence remains an explicit parity limitation until the later v3.2.1 fixture is recovered.

## 8. Recovered Family/Safety semantics

The implemented recovered v3 Family structure is:

- baggage 30%;
- by-fit 25%;
- child-seat/stroller 30%;
- Euro NCAP child protection 15%.

UNKNOWN child-protection evidence is excluded and the Family denominator is renormalized. Safety has no standalone dimension: the hard safety requirement is a gate; the child-protection gradient is capped inside Family.

The generic engine has the primitives to represent this structure. Exact v3.2.1 profile parity remains fixture-dependent.

## 9. Lease economics

Base cash cost:

`upfront + recurring_payment × months + mandatory_fees`

Mileage fit compares expected annual km with contracted annual km over the term.

- If expected km exceeds contracted km and overage pricing is unavailable, overage cost and adjusted total are UNKNOWN/None.
- If expected km is below contracted km and no explicit unused-km value assumption exists, unused-km loss and adjusted total are UNKNOWN/None.
- An unused-km value assumption MUST use `<offer currency>/km`; a currency/unit mismatch is UNKNOWN and blocks readiness.
- Missing or UNKNOWN decision-critical lease evidence blocks readiness.

The economics layer emits provenance-bearing derived attributes such as `economics.base_cash_cost` and `economics.total_adjusted_cost`, which can enter the canonical criterion pipeline.

### Historical liquidity clarification

Recovered v2.1 used a standalone liquidity **score**, not a gate: preferred first payment 30,000 DKK; preferred first-12-month cash burden 85,000 DKK; 50/50 threshold-fit versus relative-to-cheapest blend. The full recovered v3 five-dimension model does not expose a standalone Liquidity dimension or liquidity gate. Engine v0.1 MUST NOT invent one as canonical v3 semantics.

## 10. Entity separation

Vehicle, offer and derived attribute domains may not silently overwrite one another. Key collisions are rejected.

## 11. Units and currency

Canonical lease units:

- term: `month`
- annual mileage: `km/year`
- upfront payment and mandatory fees: offer currency
- recurring payment: `<currency>/month`
- overage rate: `<currency>/km`

A criterion may declare an expected unit. Mismatches are non-scorable, not evidence-sufficient, and block readiness. Rank-eligible candidates in different currencies cannot be ranked together without an explicit conversion layer.

## 12. Ranking and close calls

Deterministic display order is eligibility class, score descending, evidence coverage descending, then `candidate_id` ascending.

The internal score remains 0–10 for compatibility with Revision A falsification bands:

- gap ≤ 0.20 when applicable coverage <95%;
- gap ≤ 0.15 when applicable coverage ≥95%.

The leader is tested against all rank-eligible contenders. Ranking recomputes close-call state on every invocation to prevent stale state. A close call makes the affected recommendation surface NOT_READY.

## 13. Purchase economics

`BUY_NEW` and `BUY_USED` remain method-blocked. Do not implement decision-ready purchase economics until the exact Acquisition/Purchase Draft A, exact P1–P3 adversarial findings, and **purchase-layer** Economics Floor/Need/Stretch anchors are recovered and resolved; residual scenarios and break-even residual logic must then be validated with financing cash-flow/economic-cost reconciliation tests.

Loan principal remains separate from economic cost.

Recovered vehicle utility anchors in section 5 are not purchase economics anchors.

## 14. Validation and QA

The regression suite falsifies the generic engine contract plus recovered v3 semantics, including:

- multiplier mapping;
- explicit Need utility and recovered v3 Need=0.8;
- missing-data denominator behavior;
- data vs decision-sufficient evidence coverage;
- inactive/excluded weight visibility;
- dimensions/subweights/caps;
- prevention of positive-weight dead criteria;
- gate PASS/FAIL/UNKNOWN;
- recovered v3 UNKNOWN-gate rank eligibility + NOT_READY behavior;
- recovered v3 FAIL-gate ineligibility;
- MUST_HAVE cannot become gate-only;
- MODELED cannot be VERIFIED;
- scenario-adjusted economics cannot self-promote to VERIFIED and retains lineage;
- 94.9%/95.0% close-call boundary under current Revision A coverage semantics;
- generic stricter UNKNOWN-gate blocking policy remains available;
- purchase-blocked candidates cannot outrank rank-eligible candidates;
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

The recovered workbook frontend separately requires Excel/LibreOffice compatibility QA.

## 15. Non-goals

v0.1 does not include live scraping, a complete source-freshness service, unresolved purchase assumptions, UI/Excel generation, probabilistic residual forecasting, automatic source verification, or a claim of v3.2.1 parity before its exact fixture is recovered.

## 16. Release condition

Engine v0.1 may merge only when:

1. CI is green on the current PR head;
2. adversarial review is rerun on that same head after source recovery;
3. no unresolved P0 remains;
4. remaining P1/P2 limitations and recovered spec/implementation conflicts are explicit and do not silently weaken a binding decision.
