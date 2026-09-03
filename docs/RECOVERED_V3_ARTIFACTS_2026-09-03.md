# Recovered Leasingmatrix v3 artifacts — 2026-09-03

**Status:** source-recovery note for PR #2 and Issue #1. This document distinguishes exact recovered artifacts from still-missing originals. It does not claim v3.2.1 recovery where the artifact itself does not say v3.2.1.

## Recovered in the migration environment

### Workbooks

- `Leasingmatrix_2026_v2.1(3).xlsx`
  - SHA-256: `42d8fa904db4a943fb4e31e4c1bd375769e9c7e6710085eaf7220715aa43eb35`
  - 21 sheets.
  - Confirms the interim v2.1 liquidity score and thresholds: preferred max first payment 30,000 DKK; preferred max first-12-month cash burden 85,000 DKK; 50/50 blend between threshold score and relative-to-cheapest score.

- `Leasingmatrix_2026_v3(3).xlsx`
  - SHA-256: `6c9ec3f1f341ba7100f67b2796a39ff23532e674eefe523d126117fd6dd0dab3`
  - 34 sheets.
  - `Vehicle_Data` extends to row 146.
  - 3,117 worksheet formulas.
  - no `_xlfn.` formulas and no banned `XLOOKUP/XMATCH/FILTER/SORT/UNIQUE/SEQUENCE/LET/LAMBDA/RANK.EQ` formulas detected by package scan.
  - internal `Change_Log` contains v3.0, v3.1 and v3.2 entries; no `v3.2.1` marker was found in the workbook package.

### Build / QA code

- `build_v3(1).py`
  - SHA-256: `ecdc7dcb9cda96b13a536c0235603a598f973131260066189913fe97f1961e41`
- `regress_v3(1).py`
  - SHA-256: `3044945151dbcf728e3708435c93cfe6e32fc246d00d15f5c53a52992ec05fee`
- `verify_v3(1).py`
  - SHA-256: `c0f8542c47db4108c475cfa3e433cec8df5af68ea958c98def2e224426ad8579`

These scripts are the earlier v2/v2.1 → v3 refinement/build verification tools, not proven to be the later bundled v3.2.1 harness.

### Exact handover/review documents recovered

- `HANDOVER_ADDENDUM_v3_RevA(1).md`
- `HANDOVER_v3_implementation(1).md`
- `REVIEW_Leasingmatrix_v3(1).md`
- `REVIEW_sweep_plus_subagent_plan(1).md`
- `REVIEW_WORKING_plus_COVERAGE_SPEC(1).md`
- `SPEC_REVIEW_v3_handover(1).md`
- `Leasingmatrix_2025-2026_complete_handover.zip` containing the original 2025/2026 handover bundle.

## Canonical corrections recovered from the originals

### Revision A numbering

The exact Revision A decisions are:

- D-V3.21 — Must-have spawns a gate and is weighted as Very High.
- D-V3.22 — label→weight mapping.
- D-V3.23 — coverage-dependent close-call threshold.
- D-V3.24 — Safety = gate + capped child-protection evidence inside Family; no standalone safety weight.
- D-V3.25 — Readiness depends on decision-critical unknowns + close-call state.
- D-V3.26 — every gate requires an operational definition.
- D-V3.27 — piecewise-linear Floor/Need/Stretch utility.
- D-V3.28 — modeled real range is ESTIMATED; VERIFIED requires matched measurement.
- D-V3.29 — evidence collection scope is shortlist/gates/promotion triggers.
- D-V3.30 — inert/excluded weights and total coverage must be visible.

The reconstructed `docs/DECISIONS.md` currently shifts several of these decision numbers and should be corrected from the exact addendum.

### Need utility is known

Revision A explicitly fixes the utility anchors to:

- Floor → 0 points
- Need → 8 points
- Stretch → 10 points

Therefore the canonical v3 Need utility is `0.8` on a 0–1 engine scale. Keeping `need_utility` configurable may still be useful generically, but the v3 compatibility profile must use 0.8 and documentation must not state that the value is unrecovered.

### Gate UNKNOWN remains ranked in historical v3

The implementation handover states:

- gate FAIL → INELIGIBLE;
- a missing NCAP result produces an UNKNOWN gate and the model remains ranked.

The recovered workbook implements `Eligible = 1` when no gate equals `FAIL`; UNKNOWN gate states do not remove ranking eligibility. UNKNOWN is handled through Confidence/Readiness.

This falsifies the current Engine v0.1 assumption that every decision-critical UNKNOWN should set candidate eligibility to `BLOCKED`.

### Safety / Family profile is recovered for implemented v3

Recovered `Parameters` and `Scoring_Engine` establish:

- Family weights: 30% baggage, 25% by-fit, 30% child-seat/stroller, 15% child protection.
- UNKNOWN child-protection evidence is excluded and the Family denominator is renormalized.
- NCAP gate: >= 5 stars and protocol year >= 2020.
- child-protection gradient: 70% → 0 points, 95% → 10 points.

This closes the generic statement that Safety/Family semantics are wholly unrecovered for v3/v3.2. Exact v3.2.1 parity is still pending.

### Liquidity clarification

The recovered v2.1 workbook contains a **liquidity score**, not a gate:

- preferred first payment: 30,000 DKK;
- preferred first-12-month cash burden: 85,000 DKK;
- score blends threshold fit and relative-to-cheapest using a 50% mix parameter.

The full recovered v3 architecture collapses the score model to five dimensions and does not implement a separate liquidity gate. The reconstructed statement that an unrecovered v3 "liquidity guard" blocks parity should therefore be removed or reframed as historical v2.1 semantics unless a later v3.2.1 source proves otherwise.

## Important contradiction still unresolved

Revision A D-V3.23 defines the close-call 95% switch using **evidence-weight coverage**. The recovered v3/v3.2 workbook instead calculates `Coverage = critical_evidence_ok / 4` from four critical checks (fresh offer, NCAP, insurance quote, family test) and uses that value for the 95% threshold.

Do not silently choose between the specification and the implementation. The missing v3.2.1 workbook/harness may contain the correction that resolves this conflict.

## Still missing / not proven recovered

1. Exact v3.2.1 workbook/build referenced by the later review.
2. Bundled v3.2.1 QA harness.
3. Latest v3.2.1 QA harness output.
4. Acquisition & Purchase Layer Draft A source text.
5. Exact adversarial Purchase P1–P3 findings/wording.
6. Purchase-layer Economics Floor/Need/Stretch anchors. The recovered range/DC/baggage anchors are vehicle-utility anchors and must not be mistaken for purchase economics anchors.

## Immediate consequence for PR #2

The prior merge recommendation is superseded. Before merge:

1. represent historical v3 semantics where gate UNKNOWN remains rank-eligible but not READY;
2. set the canonical v3 Need utility to 0.8 in the compatibility fixture/profile;
3. correct reconstructed decision numbering and liquidity claims;
4. add a recovered-v3 parity fixture from the v3/v3.2 workbook;
5. keep the close-call coverage conflict explicit until v3.2.1 is recovered;
6. rerun adversarial review on the new head.
