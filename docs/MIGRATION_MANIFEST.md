# Migration Manifest

Migration started: **2026-09-02**

The purpose of this manifest is to distinguish exact imported artifacts from reconstructed project documentation. Missing originals are never presented as if they had been recovered.

## Available original source artifacts

### `2025 leasing matrix.xlsx`

Status: **available in migration environment; binary commit pending**

Observed workbook structure:

- 1 sheet: `Ark1`
- used range: `A1:H34`
- compared vehicles include Polestar 2, Tesla Model Y, BMW iX1 xDrive30 M Sport, Kia Niro EV, Skoda Elroq 85 and Kia EV3 Upgrade;
- contains economics, operating cost, specifications and a small household-needs section.

This file is a historical/personalized baseline, not the canonical 2026 decision engine.

### `IONIQ_5_privatleasing.pdf`

Status: **available in migration environment; binary commit pending**

Source characteristics:

- Hyundai IONIQ 5 private-leasing price list;
- source price list last updated 2024-12-18;
- prices stated as valid for registrations after 2025-01-01 through 2025-06-30;
- multiple variants and annual-mileage bands;
- therefore historical source evidence, not a current September 2026 offer.

## Previously referenced project artifacts pending exact import

The following filenames were part of the prior project/review flow but their exact bytes are not currently available to this repository migration:

### Workbooks

- `Leasingmatrix_2026_v2.1(2).xlsx`
- `Leasingmatrix_2026_v3(2).xlsx`
- `Leasingmatrix 2026 v3.xlsx`
- v3.2.1 workbook/build referenced in later review

### Build / QA code

- `build_v3.py`
- `regress_v3.py`
- `verify_v3.py`
- bundled v3.2.1 QA harness
- most recent QA harness output

### Handover / review documents

- `HANDOVER_ADDENDUM_v3_RevA.md`
- `HANDOVER_v3_implementation.md`
- `REVIEW_Leasingmatrix_v3.md`
- `REVIEW_sweep_plus_subagent_plan.md`
- `REVIEW_WORKING_plus_COVERAGE_SPEC.md`
- `SPEC_REVIEW_v3_handover.md`
- Acquisition & Purchase Layer Draft A source text
- adversarial review / handover for Acquisition & Purchase Layer

### Required unresolved anchor inputs

The exact current **Economics Floor / Need / Stretch** anchor values are pending import. Until those are recovered, purchase-layer implementation should not be promoted as canonical.

## Reconstructed canonical docs in this repository

The following files summarize decisions and project state from the reviewed project history. They are migration documentation, not byte-identical copies of prior handovers:

- `README.md`
- `docs/PROJECT_CHARTER.md`
- `docs/METHOD.md`
- `docs/DECISIONS.md`
- `docs/VERSION_HISTORY.md`
- `docs/QA_AND_VALIDATION.md`
- `docs/ACQUISITION_PURCHASE_LAYER.md`
- `docs/MIGRATION_MANIFEST.md`

## Migration completion criteria

The migration should not be called complete until:

1. the canonical v3/v3.2.1 workbook is committed;
2. build and QA scripts are committed;
3. latest QA output is committed or reproducibly regenerated;
4. Revision A and implementation handovers are imported verbatim;
5. purchase-layer P1-P3 findings and economics anchors are recovered;
6. source artifacts have provenance/date metadata;
7. a clean-room clone can reproduce the documented checks.