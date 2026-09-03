# Adversarial Review — Engine 0.2.0 / v3 compatibility

**Date:** 2026-09-03  
**Branch:** `validation/v3-parity`  
**Release candidate:** Engine `0.2.0`  
**Review mode:** source recovery + falsification + implementation challenge

## Verdict

**PASS for merge once final same-head CI is green. P0 = 0.**

This verdict applies to the recovered-v3 compatibility infrastructure and the `3.2.1-R` reconstruction contract. It does **not** establish exact historical v3.2.1 parity or unblock purchase economics.

## Adversarial findings and disposition

### PC-07 — expired ACTIVE offer could remain PASS — FIXED

Recovered v3.2 computes freshness `EXPIRED` when `Gyldig til` has passed, while the recovered offer gate tests only `STALE` in the ACTIVE branch. The observed behavior is preserved in the compatibility track; the canonical/reconstructed path fails expired offers.

### PC-08 — family Dealbreaker formula reads Date row — FIXED

Recovered v3.2 reads PRØVEKØRSEL row 26 for the Dealbreaker YES check although Dealbreaker is row 25. Observed behavior is preserved; corrected path uses row 25.

### PC-09 — lease-terms gate checks minimum price only — FIXED

Revision A requires an operational gate. The corrected path now requires actual binding period, user maximum binding period, minimum price, termination evidence and return evidence. Missing evidence is UNKNOWN; known non-compliance is FAIL.

### Derived evidence could overstate NCAP certainty — FIXED

A derived NCAP result with a missing required component could inherit the remaining component's evidence grade. Missing required components now force derived evidence to UNKNOWN while retaining lineage.

### NaN / infinity could enter compatibility gate numerics — FIXED

NCAP and lease-term numeric inputs are finite-checked. Non-finite data becomes UNKNOWN rather than passing comparisons.

### Truthy strings could impersonate booleans — FIXED

Python treats non-empty strings such as `"NEJ"` and `"NO"` as truthy. Canonical family and lease-term gates now require actual `bool` values and explicit `FamilyTestState` values; wrongly typed inputs become UNKNOWN.

### Binary artifact transport could create a false fixture — FIXED AS PROCESS CONTROL

An attempted GitHub connector binary write produced a non-XLSX blob. CI rejected it. The corrupt blob was deleted; the expected SHA was not changed. The repository now pins the genuine generated artifact's hash and contains an executable validator. Byte-safe binary Git/Git-LFS import remains an explicit transport task.

## Intentionally unresolved

### PC-01 — 95% close-call coverage authority

Revision A specifies evidence-weight coverage. Recovered v3.2 uses the four critical checks. Both are represented explicitly; Engine 0.2.0 refuses to choose whichever rule happens to match a historical score.

### Exact historical v3.2.1 artifact/harness

Not recovered. The generated `3.2.1-R` is separately labelled and fingerprinted. `v3.2.1-parity-verified` remains prohibited.

### Purchase/new-buy/used-buy economics

Still blocked pending the original P1–P3 findings and purchase-layer Economics anchors, or a future explicit re-adjudication. No vehicle-utility anchor is substituted for a missing purchase-economics anchor.

## Release acceptance

Merge is allowed only if the final branch head after this review passes GitHub Actions. The release claim is:

> Engine 0.2.0 is an audited historical-compatibility release for recovered Leasingmatrix v3/v3.2 semantics, with a validated and explicitly reconstructed `3.2.1-R` compliance contract.

The release claim is not:

> Engine 0.2.0 is an exact historical v3.2.1 reproduction or a production-complete lease-versus-buy system.
