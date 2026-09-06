# Production Readiness — GLASSBOX-AUTO

**Release line:** Engine 0.2.x  
**Current production baseline:** 0.2.0 on `main`  
**Candidate:** 0.2.1 gate/claim alignment  
**Scope:** leasing decision engine and recovered-v3 compatibility

## 1. What "live" means

A release is live when all of the following are true:

1. `main` contains the reviewed implementation;
2. core, historical-compatibility, release-integrity and full-regression CI jobs are green on the same commit;
3. package metadata, runtime `__version__` and release notes agree;
4. no P0/P1 release blocker is open for the leasing scope;
5. historical/reconstructed artifacts preserve provenance and claim boundaries;
6. known limitations are public and do not silently change recommendation semantics.

A green feature or patch branch is a release candidate, not a live release.

"Live" does **not** mean that every future acquisition mode is implemented. `BUY_NEW` and `BUY_USED` remain outside the leasing production boundary until their method is source-backed and separately released.

## 2. Go-live gates

| Gate | Requirement | 0.2.x status |
|---|---|---|
| Core contracts | scoring, weights, gates, evidence, economics and ranking tests pass | REQUIRED |
| Gate semantics | `FAIL` is ineligible; decision-critical `UNKNOWN` is rank-eligible but `NOT_READY` by default; strict fail-closed ranking is explicit opt-in | REQUIRED from 0.2.1 |
| Historical compatibility | recovered-v3 / 3.2.1-R parity and difference tests pass | REQUIRED |
| Release integrity | package compiles; wheel metadata and runtime version agree; provenance guard passes | REQUIRED |
| Full regression | every repository test passes after the classified jobs | REQUIRED |
| Purchase fail-closed | unsupported purchase modes cannot masquerade as production economics | REQUIRED |
| Provenance | `3.2.1-R` cannot be relabelled as historical byte-identical v3.2.1 | REQUIRED |
| PC-01 disclosure | close-call coverage authority conflict remains explicit until source evidence resolves it | REQUIRED |

Any failure in these gates is a release blocker. Do not weaken a test merely to restore green.

## 3. CI incident classification

GitHub Actions uses four named jobs so notification emails identify the failure domain:

- `contracts / core engine` — canonical engine semantics;
- `contracts / recovered v3 compatibility` — historical source-track and parity surface;
- `release / integrity and package smoke` — packaging, version and provenance;
- `regression / full suite` — cross-suite or newly added tests not covered by the first three groups.

When a job fails:

1. read the failing test and short traceback;
2. classify it as implementation regression, intended falsifier, source conflict, environment/tooling failure or corrupted artifact;
3. fix the cause or document the source conflict;
4. add/retain a regression test;
5. require a green run on the new head before merge.

A re-run without a diagnosis is not evidence of correctness.

## 4. Gate and recommendation claim boundary

Binding Revision A D-V3.25 separates eligibility from readiness:

- gate `FAIL` → ineligible;
- decision-critical gate `UNKNOWN` may remain in the ranking, but cannot be READY;
- non-critical gaps affect Confidence/evidence rather than readiness;
- a stricter fail-closed ranking policy is allowed only when explicitly requested by the caller and must not be described as the canonical Revision A default.

This distinction is decision-relevant: `UNKNOWN` means "insufficient evidence to be ready," not "known failure."

## 5. Release claim boundary

Allowed production claim after a version is merged and green on its exact `main` commit:

> GLASSBOX-AUTO Engine 0.2.x is a tested, auditable leasing decision-engine substrate with explicit recovered-v3 compatibility controls and preserved 3.2.1-R reconstruction provenance.

Not allowed:

- calling an unmerged candidate live;
- historical v3.2.1 byte parity;
- live-market freshness unless offer evidence was actually refreshed;
- production purchase/new-buy/used-buy economics;
- VERIFIED evidence derived from assumptions or inferred data;
- describing decision-critical `UNKNOWN` as a failed gate under the canonical Revision A policy.

## 6. Workbook artifact status

`3.2.1-R` remains fingerprinted historical reconstruction evidence. Its manifest, reconstruction record and validator stay protected by release-integrity checks.

The planned public import/distribution of the reconstructed XLSX was **retired on 2026-09-06**. The retirement does not alter its pinned SHA-256 or provenance claim; it means the raw workbook is no longer a release/distribution task. Do not create a Git/LFS allowlist, release asset or replacement hash merely to publish it.

The separate private `3.2.1-RC1` workbook review track is not an Engine release artifact. Any future public demo workbook needs synthetic inputs, its own fingerprint and fresh QA.

## 7. Operational decision

The leasing engine can be released independently of:

- recovery of the missing historical v3.2.1 binary/harness;
- public distribution of the retired `3.2.1-R` binary;
- purchase-layer P1-P3 and Economics anchors;
- future live-market ingestion/frontends;
- completion of the separate private RC1 workbook review.

Those items must not be represented as completed production scope unless their own gates are satisfied.
