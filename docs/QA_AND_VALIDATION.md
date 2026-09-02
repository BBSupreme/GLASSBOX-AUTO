# QA and Validation Contract

GLASSBOX-AUTO should treat QA as part of the decision method, not as an implementation afterthought.

## Known v3 validation state before migration

The last reviewed Leasingmatrix 2026 v3 state reported:

- 809 formulas with 0 formula errors;
- independent Python verification with 0 deviations;
- 15/15 regression checks passing.

These figures describe the previously reviewed workbook state. The exact workbook and harness output must be re-imported before this repository can reproduce those claims independently.

## Required QA layers

### 1. Schema and mapping

Verify that source fields map into the canonical model without silent renaming, dropping, coercion or unit changes.

Tests should cover:

- make/model/variant identity;
- pricing fields;
- annual mileage;
- term and upfront payment;
- range and battery values;
- dimensions/cargo where used;
- evidence grade and source metadata.

### 2. Utility curves

Every Floor / Need / Stretch utility curve requires boundary tests at and around all anchors.

Tests must prove:

- monotonicity where intended;
- capped utility where intended;
- no discontinuities unless explicitly designed;
- deterministic handling of blank/missing values.

### 3. Gates

Each gate requires tests for:

- pass;
- fail;
- unknown evidence;
- missing field;
- threshold boundary;
- required evidence grade.

### 4. Weighting

Verify:

- label-to-multiplier mapping;
- exclusion of missing-data criteria from the scored denominator;
- exposure of missing coverage;
- Must-have = Very High weight + gate;
- inert/excluded weights are visible.

### 5. Ranking

Ranking must be deterministic.

Explicitly test:

- exact ties;
- near ties;
- close-call thresholds at 94.9%, 95.0% and above evidence coverage;
- stable secondary ordering.

### 6. Economics

For leasing:

- upfront payment treatment;
- monthly payment treatment;
- service/mandatory fees;
- contracted mileage;
- unused-km penalty logic;
- overage assumptions where modeled.

For purchase:

- principal is not economic cost;
- interest and fees are costs;
- residual value affects economic cost/equity;
- scenario residuals reconcile;
- break-even residual is reproducible.

### 7. Compatibility

The canonical workbook implementation must be checked in both:

- Microsoft Excel;
- LibreOffice.

Compatibility testing should include formula behavior, sorting/ranking, validations, named ranges and visible layout.

### 8. Frontend hard-code scan

Any user-facing implementation must be scanned for duplicated business logic or hard-coded thresholds that can drift from the canonical model.

## Release rule

A high numerical score does not override a failed QA contract. A release should be blocked where a known defect can materially alter ranking, gates, evidence coverage or economics.