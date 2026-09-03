# Leasingmatrix v3.2.1 Reconstruction Record

**Date:** 2026-09-03  
**Artifact status:** `RECONSTRUCTED`  
**Workbook label:** `3.2.1-R`  
**Authority:** Revision A + recovered v3.2 workbook + recovered implementation/QA evidence  
**Not a claim of:** byte-identical recovery of the historical v3.2.1 artifact

## 1. Search result

The project/File Library, local migration bundle and public GLASSBOX-AUTO repository were searched for an artifact that identifies itself as the historical `v3.2.1` workbook/build or its exact bundled QA output.

No such byte-identical artifact was found.

Recovered material does include the later v3 workbook whose internal `Change_Log` reaches `3.2`, Revision A, the implementation handover, the earlier build/verify/regression scripts and review records. That is enough to construct a controlled compliance patch, but not enough to relabel the result as the missing original.

## 2. Source fingerprints

| Artifact | Role | SHA-256 |
|---|---|---|
| recovered `Leasingmatrix_2026_v3(3).xlsx` | v3.2 observed workbook base | `6c9ec3f1f341ba7100f67b2796a39ff23532e674eefe523d126117fd6dd0dab3` |
| recovered Revision A | binding method decisions | `d826d621393010db681d553d6d936d6e02f51107e8a660130c04629e567ce8f5` |
| `Leasingmatrix_2026_v3.2.1_RECONSTRUCTED.xlsx` | generated compliance fixture | `db5d2e8b6429df4229911f6459140ff8d36d8b258609be15a905d4487fc9b972` |

The reconstructed workbook is stored under `fixtures/v3/` and must keep the `RECONSTRUCTED` suffix unless an actual historical artifact is recovered and independently fingerprinted.

## 3. Patch scope

The reconstruction is deliberately narrow. It does not expand or refresh the market catalogue.

### PC-07 — expired active offer could pass

Recovered v3.2 computes `EXPIRED` in `Offers_Data` when `Gyldig til` has passed, but the offer gate in `Scoring_Engine` checked only `STALE` for ACTIVE offers. The reconstructed gate fails EXPIRED/HISTORICAL, checks STALE/EXPIRING and passes only ACTIVE+FRESH.

### PC-08 — family Dealbreaker row mismatch

Recovered v3.2's family gate read row 26 (`Dato`) for `YES` although the `Dealbreaker?` input is row 25. The reconstructed formula reads row 25.

### PC-09 — lease-terms gate underimplemented

Recovered v3.2 passed the terms gate whenever `Mindstepris i binding > 0`. Revision A requires an operational definition containing:

- user's maximum binding period;
- known actual binding period;
- known minimum price in binding;
- known termination terms;
- known return/hand-back terms.

`3.2.1-R` therefore adds explicit inputs for those values. Missing required evidence remains `UNKNOWN`; a known binding-period breach or non-positive minimum price is `FAIL`; only a complete compliant set can `PASS`.

No missing input is silently filled with an assumed value.

## 4. What this reconstruction does not resolve

### PC-01 remains open

Revision A specifies the 95% close-call threshold switch using evidence **weight coverage**. The recovered v3.2 workbook implements the switch using its four critical evidence checks.

`3.2.1-R` does not guess which later historical v3.2.1 implementation existed. The compatibility layer keeps both source tracks explicit until an authoritative later artifact settles the conflict.

### Purchase layer remains blocked

This reconstruction does not implement `BUY_NEW` / `BUY_USED` economics and does not invent the missing purchase P1-P3 findings or purchase Economics anchors.

## 5. Acceptance contract

The reconstructed workbook becomes an authoritative **generated fixture**, not an authoritative recovered historical source, only when all of the following are green:

1. repository CI verifies its SHA-256;
2. CI opens the XLSX package and validates the patched X/Y/Z formula surfaces;
3. Python compatibility tests reproduce both observed v3.2 behavior and corrected canonical behavior;
4. adversarial review has no P0 findings;
5. documentation continues to distinguish `RECOVERED_V3_2`, `REVISION_A` and `RECONSTRUCTED_V3_2_1`.

Allowed claim after acceptance:

> `3.2.1-R` is GLASSBOX-AUTO's reproducible compliance reconstruction of the recovered v3.2 workbook under Revision A.

Prohibited claim:

> `3.2.1-R` is the recovered historical v3.2.1 workbook or proves bit-for-bit v3.2.1 parity.
