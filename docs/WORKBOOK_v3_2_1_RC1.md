# Workbook 3.2.1-RC1 — provenance and review record

Updated 2026-09-06. Status: **REVIEW REQUIRED**. Lease-only scope. No engine version change.

## What changed in the evidence

The September 3 reconstruction used a recovered v3.2 source. The subsequent build recovered a different file, `Leasingmatrix 2026 v3.xlsx`, whose `Change_Log!A16` says `3.2.1`, dated 29 August 2026. That later source already contains eligible-only Economics normalization, separate evidence-weight coverage, explicit close-call state, NCAP generation-match input and Must-have targets.

An internal version marker establishes observed lineage, not historical acceptance. The original bundled v3.2.1 QA harness remains unidentified. The old reconstruction manifest and `validate_reconstructed_v3_2_1` contract are intentionally unchanged; do not repin them to RC1. The package at the base repository commit is version **0.2.0**, regardless of branch names containing 0.2.1.

Exact artifact, source, checkpoint, review-package and private QA fingerprints are in [the RC1 manifest](../fixtures/v3/workbook_v3_2_1_rc1_manifest.json).

## Build scope

- PC-07: expired/historical offers fail eligibility even when marked ACTIVE; missing/future check dates remain UNKNOWN.
- PC-08: family Dealbreaker reads test row 25, not date row 26.
- PC-09: actual binding period, maximum binding, positive minimum binding price, termination and return evidence all participate. Known breaches cannot be concealed by other missing fields.
- Readiness includes critical gates, required insurance, missing overage data and close calls. UNKNOWN gates may remain rankable but block READY.
- Missing Must-have targets and incomplete Comfort/UX tests remain UNKNOWN. The new Comfort/UX minimum-average operationalization requires review.
- Missing numeric dimensions stay unknown and are excluded from applicable scoring denominators. Partial/zero advanced-weight vectors block a decision.
- Included insurance is not added twice; normal-year mileage overage contributes to first-year burden; missing stress mileage pricing stays unknown.
- Central-model references are retained across manufacturer tabs. Missing scores display UKENDT rather than passing text into ROUND.
- Catalogue scope remains 142 vehicle IDs, 24 manufacturer tabs and 14 scored offers across 37 sheets. Prices were not refreshed.

## Evidence actually executed

The private build QA report records **75/75 checks across 17 mutation scenarios**, 3,329 formulas, zero cached formula-error cells in the baseline and tested scenarios, and independent Python cost/score comparisons for all 14 offers. Additional normal-mileage scenarios exercise overage economics.

Scenarios: expired offer, family dealbreaker, excessive binding, completed readiness evidence, missing Must-have target, incomplete Comfort Must-have test, zero weights, partial weights, no eligible offers, two normal-mileage changes, missing Comfort data, missing NCAP input, insurance included, missing overage price, future evidence date and stale evidence.

These are build results from 2026-09-05, not a fresh external review or exhaustive proof. Detailed rankings, household costs and profile values remain in the private package. Excel, local repository pytest and Claude/Fable execution were **NOT RUN** at build time. Repository CI is a separate, same-commit gate; inspect its actual status before merging.

The public checker only verifies the exact artifact hash, XLSX structure, sheet/formula counts and absence of cached error cells. It does not recalculate formulas, validate economic semantics or independently reproduce the 75 checks:

```bash
python scripts/verify_workbook_rc1.py /private/path/Leasingmatrix_2026_v3.2.1_RC1.xlsx
python -m unittest discover -s tests -p test_workbook_rc1_integrity.py -v
```

## Reproducibility and privacy boundary

The owner already has `Leasingmatrix_v3.2.1_Claude_Review_Package.zip`. It contains the final workbook, source workbooks, historical attachments, binding Revision A, detailed QA, mutation scripts, a final artifact-tool repair builder, a pre-repair workbook checkpoint and a source-to-candidate cell delta.

The first temporary full builder did not survive an interruption. Final replay therefore requires the pinned checkpoint; source-only reproducibility is not claimed. Verify hashes before using dependencies. Re-exported workbooks may differ at byte level and must receive new fingerprints and QA rather than overwriting the released hash.

Work privately outside this checkout. Follow `RUNBOOK.md` inside the pinned review ZIP, setting `LEASING_PROJECT_ROOT` explicitly to the extraction directory. Its corrected contents were verified on 2026-09-06; an older loose file with the same name is not the authority. The authoring dependency is `@oai/artifact-tool`; openpyxl is used only for read-only checks. Recalculate with LibreOffice using a separate temporary user profile, generate/recalculate the mutation workbooks, then run the independent checker. Review the package inventory before claiming any other file is present.

Do not commit the ZIP, workbook, source attachments, full QA report, previews or extracted profile to this public repository. The ignore rules are a guardrail, not a privacy audit. A future public demo workbook needs a synthetic profile, its own fingerprint and fresh QA. The existing private RC1 must not be silently rewritten or mislabeled as that demo.

## Remaining release gates

1. Resolve evidence-weight coverage: AJ retains coarse inherited 50/50 evidence factors; the 95% close-call switch is not proven attribute-weight faithful.
2. Independently assess missing/invalid inputs, partial tests, ties, row reorder and ID mismatches, NCAP generation match and eligibility.
3. Attack the approximate insurance break-even with anchor-switching and zero Economics weight. Relative lease Economics is not an approved purchase anchor model.
4. Recalculate the final artifact in Excel and rerun scenario checks; verify formula compatibility and visible outputs.
5. Run same-commit repository CI separately. Do not reuse historical pass counts.
6. Execute the requested external adversarial review with a confirmed actual model identifier. No silent Fable substitution.

Purchase P1–P3 / AC-21 remain blocked. The 2025 IONIQ 5 PDF expired on 30 June 2025 and is only a historical fixture, never an active 2026 offer.

Start the review with [the Claude handover](CLAUDE_HANDOFF_WORKBOOK_v3_2_1_RC1.md).

## Repository-update verification — 2026-09-06

- `python -m unittest discover -s tests -p test_workbook_rc1_integrity.py -v`: **7/7 passed**. These are synthetic integrity-checker tests, not workbook scenario tests.
- `python scripts/verify_workbook_rc1.py <private RC1 path>`: exact hash matched; **37 sheets, 3,329 formulas, zero cached error cells**. Read-only; no recalculation in this update.
- `PYTHONPATH=src python -m glassbox_auto.release_integrity --expected-version 0.2.0 --root .`: **PASS**; older 3.2.1-R provenance guard and explicit PC-01 limitation intact.
- `python -m compileall -q src scripts` and `git diff --check`: **PASS**.
- Full local pytest suite: **NOT RUN**, because pytest is unavailable. Remote CI must be checked on the pushed commit; this record does not assert its result.
- Claude, Fable 5.1 and Excel: **NOT RUN**. No merge or release approval.
