# GLASSBOX-AUTO Engine v0.1 — Implementation Specification

**Status:** implementation candidate under adversarial review  
**Date:** 2026-09-02  
**Scope:** headless decision engine for vehicle/acquisition comparison

## 1. Objective and compliance boundary

Build an implementation-independent, deterministic decision engine whose outputs can be audited from source evidence through to recommendation.

The engine implements the binding semantics documented in `DECISIONS.md` and `METHOD.md` where those semantics are known. It MUST NOT invent missing historical v3 profile values or unresolved purchase assumptions. Exact v3 profile reproduction remains pending the original v3.2.1 workbook/harness and anchor recovery tracked in Issue #1.

Excel is a reference interface, not the source of truth.

## 2. Canonical entities

### Vehicle
Stable facts about a car/configuration. Vehicle facts MUST NOT contain offer-specific economics.

### AcquisitionOffer
A concrete acquisition offer linked to one Vehicle. Modes:

- `LEASE_NEW`
- `BUY_NEW`
- `BUY_USED`

Decision-critical lease fields — term, annual km, upfront payment, recurring payment, mandatory fees and overage rate — are `ObservedValue`s with field-level evidence and canonical units.

### UserProfile
Contains criteria, scenario inputs and explicit weighting structure.

A criterion can declare preference label, Floor / Need / Stretch utility anchors, explicit `need_utility`, gate definition, minimum evidence requirement, dimension, base weight, subweight, optional weight cap and expected unit.

Dimension weights are profile inputs. This makes the engine capable of representing established v3 structures such as editable Family subweights, an 8+2 baggage split and capped safety evidence without hard-coding the missing historical profile values into the engine.

### DecisionCandidate
A derived object containing score, gate states, criterion contributions, data coverage, decision-sufficient evidence coverage, economics, eligibility, readiness, close-call state and reasons.

## 3. Evidence contract

Evidence grades:

- `UNKNOWN`
- `ESTIMATED`
- `VERIFIED`

Evidence kinds:

- `DIRECT`
- `DERIVED`
- `MODELED`

Rules:

1. VERIFIED evidence requires a source.
2. MODELED evidence cannot be VERIFIED.
3. Deterministic derived values inherit the weakest evidence grade among required inputs and retain input-source lineage.
4. A derived value that depends materially on a user scenario or forecast MUST NOT be promoted above ESTIMATED merely because its market inputs are VERIFIED.
5. Data presence and decision-sufficient evidence are separate concepts.
6. A criterion is decision-sufficient only when its evidence meets that criterion's declared minimum grade and its unit contract is satisfied.

## 4. Preference and weighting semantics

Binding label multipliers remain:

| Label | Multiplier | Gate |
|---|---:|---|
| LOW | 0.5 | No |
| MEDIUM | 1.0 | No |
| HIGH | 1.5 | No |
| VERY_HIGH | 2.0 | No |
| MUST_HAVE | 2.0 | Yes |

Effective criterion weight is:

`base_weight × subweight × dimension_weight × label_multiplier`

An optional criterion cap is then applied.

Only active and scorable criteria enter the score denominator. Inactive/excluded criteria remain visible in `CriterionResult` with zero normalized contribution.

An active criterion with positive weight MUST have utility anchors. A deliberate gate-only criterion is represented with `base_weight=0`, a gate and no utility anchors. This prevents accidental dead weights.

## 5. Utility

Utility uses explicit piecewise-linear Floor / Need / Stretch anchors. `need_utility` is mandatory because the currently available binding documents do not establish a canonical numerical value for utility at Need.

For `HIGHER_IS_BETTER`:

- value <= Floor => 0
- Floor..Need => linear 0..`need_utility`
- Need..Stretch => linear `need_utility`..1
- value >= Stretch => 1

`LOWER_IS_BETTER` mirrors the curve.

No hidden utility anchor is permitted.

## 6. Gates and eligibility

Gate states:

- `PASS`
- `FAIL`
- `UNKNOWN`

Missing data or insufficient evidence returns UNKNOWN, not FAIL.

A MUST_HAVE criterion MUST contain both an operational gate and a scoring definition with utility anchors. This preserves Must-have = Very High weight + gate.

Candidate eligibility is separate from score:

- `ELIGIBLE` — no failed gate and no decision-critical blocker;
- `BLOCKED` — unresolved gate, incomplete economics, unit mismatch, purchase-method blocker, no score, or another decision-critical unknown;
- `FAILED` — at least one failed gate.

Only ELIGIBLE candidates can be promoted or participate in close-call formation.

## 7. Coverage

Two weighted coverage measures are exposed.

**Data coverage** is the weight share where a value is present.

**Evidence coverage** is the weight share where a value is present, meets the criterion's minimum evidence requirement and satisfies any declared unit contract.

The close-call 95% boundary uses decision-sufficient evidence coverage, not mere data presence.

## 8. Lease economics and scoring integration

Lease economics calculates:

`base_cash_cost = upfront + recurring_payment × months + mandatory_fees`

Mileage treatment compares expected annual km with contracted annual km over the lease term.

If expected km exceeds the contract and no overage rate is available, overage cost is `None/UNKNOWN`, not zero.

If expected km is below the contract and no explicit unused-km value assumption is supplied, unused-km value loss is `None/UNKNOWN`, not zero.

Decision-relevant missing or UNKNOWN economic evidence blocks readiness.

The economics layer publishes derived attributes including:

- `economics.base_cash_cost`
- `economics.total_adjusted_cost`

These enter the same canonical criterion pipeline as vehicle and offer attributes. A profile can therefore weight and score economics without frontend duplication of business logic.

`economics.total_adjusted_cost` retains derivation lineage. Where expected mileage changes economic cost, the output is scenario-dependent and is capped at ESTIMATED even if all offer-price inputs are VERIFIED.

## 9. Entity separation

Vehicle and offer attributes may not silently overwrite each other. Attribute-key collisions are rejected. Derived economics attributes are also collision-checked.

Future schema namespacing may make domains explicit, but silent overwrite is prohibited in v0.1.

## 10. Units and currency

Canonical lease fields require normalized units before entering the engine:

- term: `month`
- annual mileage: `km/year`
- upfront payment and mandatory fees: offer currency
- recurring payment: `<currency>/month`
- overage rate: `<currency>/km`

A criterion may declare an expected unit. A present observation with a different unit is not scorable, does not count as decision-sufficient evidence and blocks candidate readiness rather than being silently coerced.

Eligible candidates in different currencies cannot be ranked together without an explicit conversion layer. v0.1 does not invent exchange rates.

## 11. Ranking and close calls

Display order is deterministic:

1. `ELIGIBLE`
2. `BLOCKED`
3. `FAILED`
4. score descending within eligibility class
5. evidence coverage descending
6. `candidate_id` ascending

Blocked or failed candidates cannot become recommendation leaders by score alone.

The internal score remains on a 0–10 scale for compatibility with historical close-call bands:

- gap <= 0.20 when pairwise evidence coverage < 95%;
- gap <= 0.15 when pairwise evidence coverage >= 95%.

For each eligible contender, pairwise coverage is the conservative minimum of leader and contender decision-sufficient evidence coverage.

The leader is checked against **all eligible contenders**, not only row #2. Every eligible candidate within the falsification band is marked close-call and NOT_READY at recommendation level.

Ranking recomputes ranking-level close-call state on every invocation so reused results cannot retain stale close-call flags.

## 12. Purchase economics

`BUY_NEW` and `BUY_USED` remain method-blocked.

Do not implement decision-ready purchase economics until:

1. original P1–P3 findings are imported and resolved;
2. economics Floor / Need / Stretch anchors are recovered;
3. residual scenarios and break-even residual logic are validated;
4. financing cash-flow and economic-cost reconciliation tests exist.

Loan principal remains explicitly separate from economic cost.

## 13. Input validation

Negative economic values are rejected where impossible; lease term must be positive. Canonical economic units are validated at offer construction. Cross-currency eligible ranking is rejected without conversion.

## 14. QA acceptance criteria

CI MUST include falsification tests for at least:

- label multiplier mapping;
- explicit Need utility;
- missing-data score denominator;
- data coverage vs decision-sufficient evidence coverage;
- inactive/excluded weight visibility;
- dimension/base/subweight/cap representation;
- prevention of positive-weight unscored/dead criteria;
- gate PASS/FAIL/UNKNOWN and evidence thresholds;
- MUST_HAVE cannot be gate-only;
- MODELED cannot be VERIFIED;
- scenario-adjusted economics cannot self-promote to VERIFIED and preserves lineage;
- 94.9% / 95.0% close-call boundary;
- UNKNOWN-gate candidate cannot outrank PASS candidate;
- purchase-blocked candidate cannot rank first;
- failed/blocked candidate cannot create close call;
- three or more eligible candidates inside falsification band;
- ranking close-call state is recomputed idempotently;
- economics-derived cost changes ranking when configured as a criterion;
- lease cash reconciliation;
- missing overage pricing is UNKNOWN, not zero;
- missing unused-km value assumption is UNKNOWN, not zero;
- UNKNOWN decision-critical economics blocks completeness;
- vehicle/offer attribute collision rejection;
- negative economics input rejection;
- canonical economic unit rejection;
- criterion unit mismatch blocks readiness;
- cross-currency eligible ranking rejection;
- deterministic final tie ordering.

## 15. Non-goals for v0.1

- live scraping;
- unresolved purchase assumptions;
- UI/Excel generation;
- automatic source verification;
- probabilistic residual forecasting;
- reconstructing missing v3 anchors from memory;
- claiming bit-for-bit v3.2.1 reproduction before the original fixture is recovered.

## 16. Release condition

Engine v0.1 may merge only when:

1. CI is green;
2. adversarial review is rerun against the patched implementation;
3. no unresolved P0 finding remains;
4. any remaining P1/P2 limitation is explicitly documented and does not silently weaken a binding decision.
