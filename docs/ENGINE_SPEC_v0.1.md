# GLASSBOX-AUTO Engine 0.1.0 — Release Specification

**Status:** audited headless substrate  
**Release date:** 2026-09-03  
**Scope:** generic vehicle/acquisition decision engine with explicit compatibility controls for recovered Leasingmatrix v3 semantics

## 1. Compliance boundary

Engine 0.1.0 implements the generic decision primitives and source-backed semantics that can be defended from the recovered project artifacts. It does **not** claim bit-for-bit v3.2.1 parity and does not enable purchase recommendations.

Historical workbook versions and engine SemVer are separate version domains. See `VERSIONING_AND_BRANCHING.md`.

## 2. Canonical entities

- `Vehicle`: stable vehicle/configuration facts.
- `AcquisitionOffer`: offer-specific economics and evidence linked to one vehicle.
- `UserProfile`: criteria, scenario inputs, dimensions and explicit compatibility policies.
- `CandidateResult`: score, evidence/data coverage, gates, eligibility, readiness, economics, close-call state and reasons.

Vehicle, offer and derived-attribute namespaces may not silently overwrite each other.

## 3. Evidence

Grades: `UNKNOWN | ESTIMATED | VERIFIED`.  
Kinds: `DIRECT | DERIVED | MODELED`.

VERIFIED requires a source. MODELED cannot be VERIFIED. Derived values retain lineage and inherit/cap evidence grade according to their required inputs and scenario dependence. Modeled real-world range is ESTIMATED; VERIFIED requires generation/variant-matched measurement.

## 4. Weighting and utility

Recovered Revision A defaults:

- Economics 35
- Family 25
- Comfort 15
- EV Usability 15
- Equipment/UX 10

Preference multipliers: Low .5 / Medium 1 / High 1.5 / Very High 2 / Must-have 2 + gate.

Utility is explicit piecewise linear Floor → Need → Stretch. For the recovered v3 compatibility profile: Floor=0/10, Need=8/10, Stretch=10/10 (`need_utility=0.8`). Recovered defaults include range 200/350/500 km, baggage 300/profile-need/600 L and DC 10–80 45/28/18 minutes (lower is better).

Weights, anchors, thresholds and decision numerics must be finite. NaN/±infinity cannot become scorable values.

## 5. Gates, criticality, eligibility and readiness

Gate states: `PASS | FAIL | UNKNOWN`.

Every gate explicitly declares `decision_critical`. A Must-have gate is always decision-critical.

- `FAIL` → `FAILED` / ineligible.
- non-critical `UNKNOWN` does not block eligibility or Readiness; it remains an evidence/Confidence concern.
- generic default: decision-critical `UNKNOWN` → `BLOCKED` and NOT_READY.
- recovered-v3 compatibility: `unknown_gate_blocks_eligibility=False`, so decision-critical `UNKNOWN` may remain rank-eligible but stays NOT_READY.

Incompatible gate value types resolve fail-closed as UNKNOWN/type mismatch rather than raising or silently passing.

The generic substrate exposes READY / NOT_READY. Historical tri-state READY / NEARLY READY / NOT READY and first-class Confidence are deferred to the compatibility/parity layer.

## 6. Coverage and close calls

Data coverage and decision-sufficient evidence coverage are separate weighted measures.

Engine 0.1.0 follows binding Revision A for the close-call switch: 0.20 below 95% applicable weight coverage, 0.15 at/above 95%. The leader is checked against all rank-eligible contenders and ranking is deterministic.

The recovered v3/v3.2 workbook instead uses four critical-evidence checks for the 95% switch. This conflict remains explicit until the missing v3.2.1 fixture resolves it.

## 7. Family/Safety compatibility primitives

Recovered v3 Family configuration is 30% baggage / 25% by-fit / 30% child-seat-stroller / 15% child protection, with unknown child protection renormalized out. Safety has no standalone dimension. Recovered NCAP gate is ≥5 stars and protocol year ≥2020; generation matching remains evidence/ingestion responsibility.

## 8. Lease economics

Core base cash cost:

`upfront + recurring × months + mandatory fees`

Expected km can create explicit mileage adjustments. Over-contract km requires overage pricing. Under-use treatment is a profile policy:

- generic default `require_unused_km_value=True`: missing unused-km valuation leaves adjusted economics incomplete;
- recovered-v3 compatibility `False`: unused contracted km are explicitly **not monetized** in Economics, matching the recovered workbook; this is a declared method choice, not silent missing→zero coercion.

Historical v3 household Economics also includes energy, insurance, parking, tax/wear reserve and over-km effects. That source-backed compatibility calculation belongs in the next historical adapter, not as hidden generic defaults.

## 9. Input integrity

- canonical offer units are enforced;
- eligible cross-currency ranking without explicit conversion is rejected;
- duplicate criterion IDs are rejected;
- contracted annual km must be >0;
- non-finite canonical inputs/weights/anchors/thresholds are rejected;
- numeric strings are not silently coerced into numeric criteria/gates.

## 10. Purchase scope

`BUY_NEW` and `BUY_USED` remain structural only and method-blocked. Do not implement decision-ready purchase economics until the exact Purchase Draft A, exact P1–P3 findings and purchase Economics Floor/Need/Stretch anchors are recovered and resolved. Loan principal remains separate from economic cost; scenario residuals and break-even residual remain preserved architecture.

## 11. QA and release contract

The final v0.1 suite includes the original engine tests, recovery-source falsifiers and second-round adversarial tests covering ranking eligibility, economics integration, coverage, Must-have semantics, decision-critical/non-critical UNKNOWN behavior, v3 unused-km compatibility, type/unit failure modes, non-finite values, collision handling, deterministic ties and close-call behavior.

A decision-semantic release requires green CI and adversarial review on the same final head.

## 12. Allowed release claim

> **GLASSBOX-AUTO Engine 0.1.0 is an audited, source-recovery-corrected headless decision-engine substrate with explicit compatibility controls for recovered Leasingmatrix v3 semantics.**

Do not claim verified v3.2.1 parity. The next branch is `validation/v3-parity`.