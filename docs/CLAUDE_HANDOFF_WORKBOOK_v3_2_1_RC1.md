# Claude handover — workbook 3.2.1-RC1

## Execute this task

Act as review orchestrator for GLASSBOX-AUTO workbook **3.2.1-RC1**. Have **Fable 5.1** perform an independent adversarial review of the exact private artifact, source lineage and build evidence. Verify the actual model identifier first. If that model is unavailable or the name is ambiguous, report the blocker and request the intended identifier; do not substitute or claim a Fable review.

This handover is prepared, not dispatched to a running Claude session. No Claude/Fable execution is claimed by this repository. The repository update is authorized; this handover does not authorize a reviewer to merge, publish private material, enable purchase economics or communicate with other third parties.

## Inputs and first checks

1. Read [the RC1 record](WORKBOOK_v3_2_1_RC1.md), its [manifest](../fixtures/v3/workbook_v3_2_1_rc1_manifest.json), `docs/METHOD.md`, `docs/DECISIONS.md`, `docs/ACQUISITION_PURCHASE_LAYER.md` and `docs/PRODUCTION_READINESS.md`.
2. Obtain the already-delivered `Leasingmatrix_v3.2.1_Claude_Review_Package.zip` from the owner through the private project. This public checkout intentionally does not contain it. If missing, stop workbook review and ask for that exact package; do not reconstruct missing evidence from summaries.
3. Check the ZIP SHA-256 against the manifest before extraction. Extract into a private directory outside this checkout. Check the workbook, source, pre-repair checkpoint and QA report hashes. Run `scripts/verify_workbook_rc1.py` from this checkout against the extracted final workbook.
4. Read the package's binding Revision A, implementation handover, prior reviews, `RUNBOOK.md`, scripts and source delta. The corrected `RUNBOOK.md` inside the pinned ZIP was verified on 2026-09-06; do not use an older loose checkpoint runbook. The initial full builder was lost: final replay uses a pinned pre-repair checkpoint. Do not claim a source-only rebuild.
5. Record the actual checkout commit, workbook hash, application versions, review model identifier and which checks you independently executed. Package QA is evidence to challenge, not your own result.

## Source precedence

Owner instructions and binding Revision A (D-V3.21–D-V3.30) come first. The newly recovered internally labeled 3.2.1 source supplies established architecture and observed behavior subject to Revision A. The separate reconstructed 3.2.1-R provides narrowly reviewed PC-07/08/09 corrections, not authority to replace the new source wholesale. Repository method and compatibility code are additional evidence; implementation handovers and old pass counts are not fresh tests.

The MARKET_SWEEP workbook is a research branch with rejected duplicated profile architecture. The exploratory decision-underwriting branch does not authorize purchase scope. The 2025 attachments are historical fixtures, not current offers. Preserve the older 3.2.1-R hash and validator unchanged.

## Adversarial priorities

- Attack PC-07/08/09 with expired ACTIVE offers, future/missing dates, family failure, actual versus full-term binding, missing termination/return evidence and known breaches masked by missing fields.
- Attack gate UNKNOWN versus eligibility/readiness, missing Must-have thresholds, incomplete Comfort/UX tests, negative/zero lease duration, invalid pasted categories, bad utility anchors, partial and all-zero weights.
- Attack evidence coverage at exactly 95%, NCAP generation mismatch, partial family tests and missing nested attributes. AJ currently uses inherited 50/50 proxies; distinguish it from critical-four coverage AE.
- Attack ties, no eligible candidates, row reordering, duplicate/mismatched IDs, lookup alignment and display behavior for UKENDT scores.
- Independently recompute all 14 baseline scores/costs and mileage scenarios. Test included insurance, missing overage price, upfront costs and first-year burden. The insurance break-even is explicitly approximate; test anchor-switching and zero Economics weight.
- Recalculate the exact final artifact in Excel and LibreOffice. Test semantics as well as formula errors and front-end references. Do not infer current offer validity from the fixed historical valuation snapshot.
- Confirm the frozen catalogue count without claiming current market completeness. Do not invent purchase Floor/Need/Stretch anchors or equate remembered budget limits with those anchors.

## Required outputs

Produce `FABLE_5_1_ADVERSARIAL_REVIEW.md` only after the requested model actually runs. Otherwise produce `REVIEW_BLOCKER.md`, with model/access requirements and no attributed findings.

Each finding must contain severity, workbook cell or code location, smallest reproducible counterexample, expected versus actual behavior, practical decision impact, evidence classification and proposed correction. Distinguish independently verified findings, supported observations, assumptions and untested claims. Return **RELEASE / FIX FIRST / BLOCKED**, with explicit residual risks.

Run the supplied mutations and add new counterexamples. Run repository CI/tests separately. Green engine CI does not certify the private workbook; 75 build checks do not certify the engine or Fable review. Any workbook fix creates new candidate bytes, a new fingerprint and fresh QA. Do not rewrite provenance to make a validator pass.

Keep the detailed report and household-specific reproductions private until reviewed for public disclosure. A sanitized public finding may refer to generic synthetic inputs and exact formula locations, without publishing the owner's profile or rankings.

Before context limits, write a continuation handover containing current commit, exact artifact hashes, files changed, executed commands/results, findings, unresolved gates and the next concrete action. Never mark an unexecuted test or external review as complete.
