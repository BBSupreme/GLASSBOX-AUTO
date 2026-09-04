# Go-Live Hardening Review — 2026-09-04

**Target:** Engine 0.2.0 leasing release line  
**Branch:** `hardening/go-live-v0.2.0`  
**Review type:** adversarial operational/release review

## Verdict before fixes

**HOLD for production declaration.**

The engine itself was green, but the repository still had operational gaps that made a future failed Actions email hard to diagnose and made the public README understate/blur the actual release boundary.

## Findings and disposition

### GH-01 — one undifferentiated CI job

**Severity:** P1 release-operations risk  
**Finding:** `engine-ci` exposed a single generic `test` job. A failed notification did not tell the owner whether core semantics, historical parity, packaging/provenance or a cross-suite regression had failed.  
**Fix:** split CI into named `core engine`, `recovered v3 compatibility`, `release integrity`, and `full regression` jobs; add short tracebacks and failure-class summaries.  
**Status:** FIXED.

### GH-02 — deprecated Actions runtime noise

**Severity:** P2 observability/tooling  
**Finding:** prior runs emitted Node-runtime deprecation warnings from old major versions of `actions/checkout` and `actions/setup-python`.  
**Fix:** move to current v7 major releases.  
**Status:** FIXED, subject to green CI on this branch.

### GH-03 — no executable release-integrity gate

**Severity:** P1 provenance/release risk  
**Finding:** normal unit tests could remain green if package/reconstruction metadata drifted in a way that weakened the public claim boundary.  
**Fix:** add `python -m glassbox_auto.release_integrity --expected-version 0.2.0`, checking package version, manifest schema, pinned hashes, required PC-07/08/09 patches, explicit PC-01 conflict and prohibited historical-parity claims.  
**Status:** FIXED, with regression tests.

### GH-04 — public README still described bootstrap/migration state

**Severity:** P1 product-state ambiguity  
**Finding:** README still said the repository was in migration/bootstrap and conceptually listed purchase modes alongside leasing without clearly distinguishing production support.  
**Fix:** publish the 0.2.x production boundary: private leasing live when main is green; BUY_NEW/BUY_USED remain fail-closed; link production-readiness/release docs and CI failure classes.  
**Status:** FIXED.

### GH-05 — no production-readiness contract

**Severity:** P1 governance  
**Finding:** "green tests" had no single documented release decision contract.  
**Fix:** add `docs/PRODUCTION_READINESS.md` defining same-commit green gates, incident classification, claim boundaries and the no-test-weakening rule.  
**Status:** FIXED.

### GH-06 — generated 3.2.1-R XLSX not distributed byte-safely from GitHub

**Severity:** P1 artifact-distribution limitation; not a core-engine blocker  
**Finding:** expected output is pinned at SHA-256 `db5d2e8b6429df4229911f6459140ff8d36d8b258609be15a905d4487fc9b972`, but prior connector transport corrupted a binary upload.  
**Disposition:** keep manifest/validator authoritative and prohibit hash drift. Publish the raw workbook only through a byte-safe Git/Git-LFS/release-asset route. Do not treat this limitation as historical v3.2.1 recovery.  
**Status:** OPEN DISTRIBUTION TASK; disclosed.

### GH-07 — no formal GitHub Release object

**Severity:** P2 packaging/distribution  
**Finding:** repository has release notes but no GitHub Release object/tag. The connected GitHub toolset in this session exposes release reads but not release/tag creation.  
**Disposition:** release notes are committed; after the hardening merge, create a `v0.2.0` tag/release pointing to the exact green main commit using a client with release/tag write support.  
**Status:** OPEN PLATFORM TASK; does not change code correctness.

## Production claim after acceptance

If this branch is green and merged, the allowed operational claim is:

> GLASSBOX-AUTO Engine 0.2.0 is production-live for the documented private-leasing engine scope, with recovered-v3 compatibility and explicit provenance/known-limitations controls.

This does not promote purchase economics, live scraping, byte-identical historical v3.2.1 parity or stale market evidence into production scope.

## Merge acceptance

Merge only if the branch head passes:

1. `contracts / core engine`;
2. `contracts / recovered v3 compatibility`;
3. `release / integrity and package smoke`;
4. `regression / full suite`.

A failure is reviewed by class and fixed or documented before merge. Re-running alone is not a disposition.
