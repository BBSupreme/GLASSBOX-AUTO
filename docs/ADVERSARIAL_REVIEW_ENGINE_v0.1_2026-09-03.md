# Adversarial Review — Engine v0.1

**Date:** 2026-09-03  
**Target:** PR #2 / `build/engine-v0.1`  
**Basis:** recovered Revision A, implementation handover, v2.1 workbook, later v3/v3.2 workbook, recovered QA scripts/reviews, and the PR implementation itself.

## Verdict

**Engine-substrate release:** PASS after the fixes in this review, subject to green CI on the final head.  
**Historical v3.2.1 parity:** NOT PROVEN.  
**Purchase recommendation support:** BLOCKED by missing source method/anchors.

The review deliberately distinguishes generic engine correctness from historical workbook parity. A green substrate release does not authorize a `v3.2.1 parity` label.

## Findings and disposition

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| AR2-P0-01 | P0 | Revision A requires each gate to declare whether it is decision-critical. Engine v0.1 treated every UNKNOWN gate as decision-critical. | **FIXED.** `GateDefinition.decision_critical`; non-critical UNKNOWN no longer changes eligibility/readiness; MUST_HAVE cannot use a non-critical gate. |
| AR2-P0-02 | P0 | Recovered v3 uses ~9,000 expected km/year against typically 15,000-km contracts without monetizing unused contracted km in the Economics score. Generic v0.1 required an unused-km value and would block the recovered profile. | **FIXED.** `UserProfile.require_unused_km_value` makes the treatment explicit. Generic default remains strict; recovered-v3 compatibility sets it `False`. |
| AR2-P0-03 | P0 | A non-finite vehicle metric such as `NaN` could pass Python comparisons and fall through a utility curve as maximum utility. | **FIXED.** Non-finite numeric values are rejected/non-scorable; weights, anchors, gate thresholds and canonical economic inputs are finite-validated. |
| AR2-P0-04 | P0 | Gate-only numeric criteria did not enforce numeric type compatibility; text `"5"` against numeric threshold `5` could throw rather than resolve UNKNOWN. | **FIXED.** Gate type contract now fails closed to UNKNOWN/type mismatch. |
| AR2-P1-01 | P1 | Revision A says non-critical UNKNOWN reduces **Confidence**, but the generic substrate has no first-class Confidence output. Zero-weight gate-only checks cannot reduce weight-based `evidence_coverage`. | **DEFERRED, EXPLICIT.** Implement in the historical compatibility/parity layer rather than pretending `evidence_coverage` is identical to Confidence. |
| AR2-P1-02 | P1 | Historical workbook has `READY / NEARLY READY / NOT READY`; generic v0.1 exposes only `READY / NOT_READY`. | **DEFERRED.** Next parity adapter owns the tri-state historical surface. |
| AR2-P1-03 | P1 | Exact Revision A D-V3.23 uses weight coverage for the 95% close-call switch; recovered v3/v3.2 workbook uses 4 critical-evidence checks. | **UNRESOLVED BY DESIGN.** Do not silently choose the later workbook behavior without the missing v3.2.1 fixture. |
| AR2-P1-04 | P1 | Historical v3 Economics score includes household energy, insurance, parking/tax/wear and over-km effects; core v0.1 lease economics currently covers lease cash + explicit mileage adjustment primitives only. | **DEFERRED.** Build as a source-backed v3 compatibility profile/adapter; do not hard-wire household assumptions into the generic engine. |
| AR2-P1-05 | P1 | Historical v3 has ACTIVE/STALE/EXPIRED offer behavior and freshness caps; v0.1 evidence carries dates but has no freshness service. | **DEFERRED.** Ingestion/parity layer. |
| AR2-P1-06 | P1 | Historical v3 gates include composite/derived checks (NCAP year + stars, family test, lease terms). Core `GateDefinition` is intentionally atomic. | **DEFERRED.** Parity adapter should derive auditable attributes and retain lineage rather than expanding core gate syntax prematurely. |
| AR2-P2-01 | P2 | Duplicate criterion IDs could make the decision-critical lookup ambiguous. | **FIXED.** Profiles require unique `criterion_id`. |
| AR2-P2-02 | P2 | A 0-km/year lease contract is nonsensical and made mileage math misleading. | **FIXED.** Contracted annual km must be strictly positive. |
| AR2-P2-03 | P2 | CI actions are referenced by version tags rather than immutable SHAs. | **DEFERRED HARDENING.** No decision-semantic impact. |

## Source-backed semantics now represented in core

- Revision A Need utility = 8/10.
- Must-have = Very High weight + decision-critical gate.
- Gate FAIL is ineligible.
- Gate UNKNOWN is distinct from FAIL.
- Non-critical UNKNOWN does not drive Readiness.
- Historical v3 can allow decision-critical UNKNOWN to remain rank-eligible while NOT_READY.
- Family/safety primitives can represent the recovered 30/25/30/15 structure and NCAP gate policy.
- Missing/invalid values cannot silently become neutral or favorable scores.

## Falsification additions in this pass

Tests now attack:

1. non-critical UNKNOWN vs decision-critical UNKNOWN;
2. MUST_HAVE criticality enforcement;
3. recovered-v3 9k-vs-15k under-use economics policy;
4. numeric-string gate inputs;
5. `NaN` vehicle metrics;
6. non-finite economic inputs/weights/anchors/thresholds;
7. zero contracted annual km;
8. duplicate criterion IDs.

## Release boundary

The acceptable v0.1 claim is:

> **GLASSBOX-AUTO Engine 0.1.0 is an audited, source-recovery-corrected headless decision-engine substrate with explicit compatibility controls for recovered Leasingmatrix v3 semantics.**

The unacceptable claim is:

> **Engine 0.1.0 reproduces Leasingmatrix v3.2.1.**

That second claim requires the next branch: `validation/v3-parity`, an exact fixture, and a source-backed compatibility adapter.
