# Migration Manifest

Migration started: **2026-09-02**  
Recovery update: **2026-09-03**

The purpose of this manifest is to distinguish exact recovered artifacts from reconstructed project documentation. Missing originals are never presented as if they had been recovered.

See `docs/RECOVERED_V3_ARTIFACTS_2026-09-03.md` for fingerprints and detailed semantic findings.

## Recovered original source artifacts

### Historical 2025 baseline

`2025 leasing matrix.xlsx` remains available in the migration environment as the historical/personalized baseline rather than the canonical 2026 engine.

### Hyundai IONIQ 5 historical source

`IONIQ_5_privatleasing.pdf` is available with provenance. The source price list was last updated 2024-12-18 and states validity for registrations after 2025-01-01 through 2025-06-30. It is historical evidence, not a current September 2026 offer.

### `Leasingmatrix_2026_v2.1.xlsx`

Status: **exact workbook recovered in migration environment; binary repository commit pending**.

Recovered semantics include the interim v2.1 liquidity score, dead-weight exclusion, baggage 8+2 treatment, unused-km penalty, editable Family subweights and deterministic ranking.

### Later `Leasingmatrix_2026_v3.xlsx`

Status: **exact workbook recovered in migration environment; binary repository commit pending**.

Observed structure:

- 34 sheets;
- 24 manufacturer sheets;
- `Vehicle_Data` through row 146;
- 3,117 worksheet formulas;
- internal `Change_Log` reaches v3.2;
- no v3.2.1 marker found in the workbook package.

This is a later artifact than the 21-sheet v3.0 implementation handover, but it is not sufficient evidence to relabel itself as v3.2.1.

## Recovered build / QA code

Exact source recovered in the migration environment:

- `build_v3.py`
- `regress_v3.py`
- `verify_v3.py`

These are the earlier v2/v2.1→v3 build/regression tools. They are **not proven to be the later bundled v3.2.1 QA harness**.

## Recovered exact handovers / reviews

Exact source recovered:

- `HANDOVER_ADDENDUM_v3_RevA.md`
- `HANDOVER_v3_implementation.md`
- `REVIEW_Leasingmatrix_v3.md`
- `REVIEW_sweep_plus_subagent_plan.md`
- `REVIEW_WORKING_plus_COVERAGE_SPEC.md`
- `SPEC_REVIEW_v3_handover.md`
- `Leasingmatrix_2025-2026_complete_handover.zip`

These originals supersede reconstructed wording where they conflict.

## Semantics now recovered

The recovered source package closes several earlier uncertainties:

- exact Revision A numbering D-V3.21–D-V3.30;
- default v3 dimension bases 35/25/15/15/10;
- Need utility 8/10 = 0.8;
- range, baggage and DC Floor/Need/Stretch anchors;
- Safety = NCAP gate + child-protection gradient inside Family;
- Family subweights 30/25/30/15 in the implemented v3;
- NCAP gate >=5 stars and protocol year >=2020;
- gate FAIL removes eligibility while gate UNKNOWN remains rankable but affects Readiness/Confidence in historical v3;
- v2.1 liquidity is an interim score using 30,000 DKK / 85,000 DKK thresholds and a 50% threshold/relative blend, not a recovered standalone v3 gate.

## Recovered conflict still requiring later fixture

Exact Revision A D-V3.23 defines the close-call 95% switch using **weight coverage**. The recovered v3/v3.2 workbook instead uses a four-item critical-evidence count.

This conflict must remain visible until the later v3.2.1 artifact/harness is recovered or an authoritative decision explicitly resolves it.

## Still missing / not proven recovered

### v3.2.1

- exact v3.2.1 workbook/build referenced in the later review;
- bundled v3.2.1 QA harness;
- most recent v3.2.1 QA harness output.

### Acquisition / Purchase layer

- exact Acquisition & Purchase Layer Draft A source text;
- exact adversarial review / P1–P3 wording;
- **purchase-layer** Economics Floor / Need / Stretch anchors.

Recovered vehicle-utility anchors must not be substituted for purchase economics anchors.

### Binary repository import

The recovered XLSX/PDF binaries are fingerprinted and available in the migration environment, but exact binary repository upload remains pending in the current connector workflow.

## Reconstructed canonical docs in this repository

These summarize the project state and must defer to recovered originals on conflict:

- `README.md`
- `docs/PROJECT_CHARTER.md`
- `docs/METHOD.md`
- `docs/DECISIONS.md`
- `docs/VERSION_HISTORY.md`
- `docs/QA_AND_VALIDATION.md`
- `docs/ACQUISITION_PURCHASE_LAYER.md`
- `docs/MIGRATION_MANIFEST.md`
- `docs/RECOVERED_V3_ARTIFACTS_2026-09-03.md`

## Migration completion criteria

Migration should not be called complete until:

1. the recovered canonical binaries are committed or otherwise retained in a reproducible source location;
2. exact recovered text/build scripts are retained verbatim;
3. the v3.2.1 workbook/harness/output are recovered or explicitly retired by authoritative decision;
4. purchase-layer Draft A, P1–P3 findings and purchase economics anchors are recovered or explicitly replaced by a new approved method;
5. source artifacts have provenance/date metadata;
6. a clean-room clone can reproduce the documented checks and distinguish historical, current, verified, estimated and missing evidence.
