# Production Readiness — GLASSBOX-AUTO

**Release line:** Engine 0.2.x  
**Scope:** leasing decision engine and recovered-v3 compatibility  
**Status:** GO when the release branch is green under the hardening CI below

## 1. What "live" means

A release is live when all of the following are true:

1. `main` contains the reviewed implementation;
2. core, historical-compatibility, release-integrity and full-regression CI jobs are green on the same commit;
3. package version and release notes agree;
4. no P0/P1 release blocker is open for the leasing scope;
5. historical/reconstructed artifacts preserve provenance and claim boundaries;
6. known limitations are public and do not silently change recommendation semantics.

"Live" does **not** mean that every future acquisition mode is implemented. `BUY_NEW` and `BUY_USED` remain outside the leasing production boundary until their method is source-backed and separately released.

## 2. Go-live gates

| Gate | Requirement | 0.2.x status |
|---|---|---|
| Core contracts | scoring, weights, gates, evidence, economics and ranking tests pass | REQUIRED |
| Historical compatibility | recovered-v3 / 3.2.1-R parity and difference tests pass | REQUIRED |
| Release integrity | package compiles, dependencies are consistent, version/provenance guard passes | REQUIRED |
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

## 4. Release claim boundary

Allowed production claim:

> GLASSBOX-AUTO Engine 0.2.x is a tested, auditable leasing decision-engine substrate with explicit recovered-v3 compatibility controls and a documented 3.2.1-R compliance reconstruction.

Not allowed:

- historical v3.2.1 byte parity;
- live-market freshness unless offer evidence was actually refreshed;
- production purchase/new-buy/used-buy economics;
- VERIFIED evidence derived from assumptions or inferred data.

## 5. Workbook artifact status

`3.2.1-R` is fingerprinted and its formula surface is executable/testable through the repository validator. The generated XLSX has SHA-256:

`db5d2e8b6429df4229911f6459140ff8d36d8b258609be15a905d4487fc9b972`

The raw XLSX is not committed through the current connector because the prior UTF-8-oriented binary transport corrupted it. This is an **artifact-distribution limitation**, not an engine or parity-method limitation. A raw binary may only be published when a byte-safe Git/Git-LFS or release-asset path preserves the pinned hash.

Until then, do not change the manifest hash to match a transported copy.

## 6. Operational decision

The leasing engine can be released independently of:

- recovery of the missing historical v3.2.1 binary/harness;
- purchase-layer P1-P3 and Economics anchors;
- future live-market ingestion/frontends.

Those items remain roadmap/source-recovery work and must not be represented as completed production scope.
