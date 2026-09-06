# RC1 source-to-build reproducibility contract

**Decision date:** 2026-09-06  
**Track:** private workbook `3.2.1-RC1`  
**Status:** CONTRACT DEFINED; EXECUTABLE SOURCE-ONLY REBUILD STILL BLOCKED BY MISSING RAW BUILD INPUTS IN THE PUBLIC CHECKOUT.

## 1. Required deliverable

The rewrite is not complete until the project contains an executable source-to-candidate builder named:

`scripts/build_workbook_v3_2_1_rc1.mjs`

This file must build a fresh RC1 candidate from the exact recovered source workbook and declared method inputs. It must **not** require the pinned pre-repair checkpoint as an authoring input.

A checkpoint-based repair script may remain as historical build evidence, but it does not satisfy source-only reproducibility.

## 2. Authoritative source boundary

The builder must fail closed unless the source workbook SHA-256 is exactly:

`003e13ea7f4e4f526e5eeecacee2524368a3187001a9fce686aec4c1692d4832`

Observed source identity:

- filename in the recovered package: `Leasingmatrix 2026 v3.xlsx`;
- internal marker: `Change_Log!A16 = 3.2.1`;
- role: established workbook architecture/data lineage subject to binding Revision A.

The source marker is provenance evidence, not proof that historical v3.2.1 acceptance criteria passed.

## 3. Method precedence

The builder must implement inputs in this order:

1. current owner decisions and binding Revision A D-V3.21–D-V3.30;
2. recovered internally marked 3.2.1 source for established workbook structure/data where it does not conflict with Revision A;
3. narrow PC-07/08/09 corrections supported by the separate `3.2.1-R` reconstruction record;
4. repository method/compatibility code as additional executable evidence;
5. historical handovers/reviews as rationale, not as fresh pass evidence.

D2 is binding: the separate `3.2.1-R` reconstructed XLSX is not an import/base for the RC1 rewrite and is not a distribution target. Its manifest and validator remain historical evidence only.

## 4. Authoring toolchain

The source-to-RC1 builder must:

- use `@oai/artifact-tool` for workbook authoring and structural changes;
- use a pinned/declared artifact-tool version or otherwise record the exact runtime dependency used;
- use openpyxl only for read-only independent inspection, never as the authoritative authoring path;
- write into a temporary working directory and never mutate the source workbook in place;
- accept explicit input/output paths rather than hidden machine-specific paths;
- require the caller to pass the source path and verify its hash before making changes.

Minimum command shape:

```bash
node scripts/build_workbook_v3_2_1_rc1.mjs \
  --source /private/path/'Leasingmatrix 2026 v3.xlsx' \
  --output /private/path/Leasingmatrix_2026_v3.2.1_RC_NEXT.xlsx
```

The exact CLI may be extended, but source/output paths and fail-closed source verification are mandatory.

## 5. Required transformation manifest

The executable builder must keep a machine-readable transformation list or equivalent structured code comments that identify every deliberate mutation from source to candidate. At minimum it must cover the RC1 surfaces already recorded in the review track:

- PC-07 expired/historical offer eligibility and missing/future evidence-date behavior;
- PC-08 family Dealbreaker row mapping;
- PC-09 actual/max binding period, positive minimum binding price, termination evidence and return evidence;
- readiness interaction with decision-critical gates, Must-have tests, insurance/overage gaps and close calls;
- missing numeric dimension exclusion and invalid/partial weight-vector blocking;
- included-insurance handling and normal-year mileage overage economics;
- central-model references across manufacturer tabs and `UKENDT` display behavior;
- source/offer ID alignment and no-eligible/tie behavior;
- evidence-weight coverage implementation, with any unresolved proxy explicitly identified rather than upgraded to a PASS claim.

A transformation that cannot be traced to source evidence, a binding decision or an explicitly approved correction must fail review rather than being silently added.

## 6. Output identity

A rebuilt candidate is **new bytes** unless it independently reproduces an already pinned fingerprint.

The builder must not overwrite `fixtures/v3/workbook_v3_2_1_rc1_manifest.json` merely because a new export differs byte-for-byte. Every new candidate must receive:

- its own SHA-256;
- build timestamp/environment record;
- source fingerprint;
- formula/sheet counts;
- QA result set;
- source-to-candidate delta;
- explicit statement whether it matches or differs from the prior private RC1 fingerprint.

Byte difference is not automatically a defect, but it invalidates reuse of the old artifact fingerprint.

## 7. Acceptance gates

Source-only reproducibility is proven only when all of the following are executed on the same newly built candidate:

1. exact source SHA verification passes;
2. builder exits successfully from source without reading the pre-repair checkpoint;
3. workbook opens as a valid XLSX and expected sheet/ID structure is preserved;
4. LibreOffice recalculation completes without formula errors;
5. Excel recalculation/visible-output review completes before release approval;
6. the mutation suite is rerun against the candidate, including expired ACTIVE, family fail, excessive binding, missing Must-have target, incomplete tests, zero/partial weights, no eligible candidates, mileage changes, missing NCAP input, insurance included, missing overage price, future evidence date and stale evidence;
7. independent non-spreadsheet economics/score checks cover all scored offers and required mileage scenarios;
8. exact-95%-coverage and close-call boundary tests pass under the approved evidence-weight definition;
9. row reorder, duplicate/mismatched IDs and deterministic ties are attacked;
10. metadata/privacy review confirms that no household-specific workbook or source package is being committed to the public repository;
11. a fresh adversarial review classifies remaining findings and returns RELEASE / FIX FIRST / BLOCKED.

Historical 75/75 build checks are useful evidence but cannot substitute for rerunning the gates on newly generated bytes.

## 8. Current blocker

The public checkout contains the RC1 manifest, integrity checker and review documentation, but intentionally does not contain the household-bearing source workbook, private review ZIP, pre-repair checkpoint, detailed QA output or source-to-candidate delta.

The recovered handover states that the initial full builder did not survive and that the existing final replay uses the pinned checkpoint. Therefore this repository cannot honestly synthesize a complete source-only builder from the public files alone.

To implement `scripts/build_workbook_v3_2_1_rc1.mjs`, the executing private environment must provide the exact recovered source workbook plus the pinned review package contents used to reconstruct the transformation set. If those inputs are unavailable, stop with `BLOCKED_SOURCE_INPUTS`; do not infer missing cell mutations from the final workbook and call the result reproducible.

## 9. Definition of done

This contract is closed only when:

- `scripts/build_workbook_v3_2_1_rc1.mjs` exists and satisfies sections 2–5;
- a source-only build is executed without checkpoint authoring dependency;
- section 7 evidence is recorded against the resulting bytes;
- the RC1 documentation is updated from "source-only reproducibility not claimed" to the narrower claim actually proven by that run.
