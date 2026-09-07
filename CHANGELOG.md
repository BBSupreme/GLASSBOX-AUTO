# Changelog

All notable engine changes are documented here. Historical workbook version labels are tracked separately from package Semantic Versioning.

## 0.2.2 — candidate prepared 2026-09-07

Activation requires a separate review, full same-commit CI and the reviewed merge on `main`. This entry and package metadata do not claim a published release.

### Corrected
- inclusive 0.15/0.20 close-call score gaps tolerate binary round-off within an explicit absolute 1e-12 score-point allowance; scores are not rounded for ranking and the 0.95 coverage switch is unchanged (#11);
- percent-encode vehicle/offer ID components and reject duplicate serialized identities and raw component pairs, preventing exact-tie warning suppression (#12);
- reject non-finite weights, sums, utility spans, economic calculations and result values rather than returning READY with NaN/Infinity (#13);
- use consistent finite summation and divide before score scaling to preserve ordinary decimal-weight inputs.

### Validation and migration
- retain the original 27 adversarial falsifiers and additional numerical/identity controls;
- full regression runs separately on Python 3.11, 3.12, 3.13 and 3.14;
- package metadata, runtime version, wheel checks and release-integrity expectations align on 0.2.2;
- legacy IDs with reserved characters must be regenerated from raw vehicle_id/offer_id; ordinary unreserved IDs are unchanged;
- preserve the source-repair history and reviewer evidence in `docs/REPAIR_CHANGELOG_0.2.2.md` and PR #14.

### Scope unchanged
- canonical and strict-opt-in UNKNOWN behavior, blocked purchase modes, PC-01 authority and historical workbook fingerprints are unchanged;
- bounded owner acceptance of ordinary attribution/history is documented in `docs/PRIVACY_SCOPE_2026-09-07.md`; sensitive data remains protected;
- this is not the public-agent CLI/interface, a market catalog or a multi-provider certification.

## 0.2.1 — 2026-09-06

### Corrected
- aligned the canonical decision-critical `UNKNOWN` gate default with binding Revision A D-V3.25: `UNKNOWN` may remain rank-eligible but is always `NOT_READY`; gate `FAIL` remains ineligible;
- retained an explicit `unknown_gate_blocks_eligibility=True` override for callers that intentionally require stricter fail-closed ranking, without presenting that override as the Revision A default;
- added regression coverage for the canonical default, explicit strict override and non-critical UNKNOWN behavior;
- aligned `glassbox_auto.__version__`, project metadata, wheel smoke checks and release-integrity expectations on 0.2.1;
- strengthened release integrity so runtime and package versions cannot silently diverge;
- tightened README and production-readiness language so an unmerged green branch is a candidate, not a live release.

### Provenance / distribution decision
- recorded D2: retire public import/distribution of the `3.2.1-R` reconstructed XLSX while preserving its manifest, reconstruction record and validator as historical provenance/compatibility evidence;
- the retired binary is no longer a Git/LFS or release-asset task and its pinned hash must not be repurposed for RC1;
- the separate private `3.2.1-RC1` workbook review track remains outside the Engine release artifact boundary.

### Scope unchanged
- lease-new economics remain the production-supported acquisition mode;
- `BUY_NEW` / `BUY_USED` remain fail-closed pending the separate purchase-method gates;
- PC-01 close-call coverage authority remains explicit and unresolved;
- no historical byte-identical v3.2.1 claim is introduced.

## 0.2.0 — 2026-09-03

### Go-live hardening — 2026-09-04
- classified CI into core-engine, recovered-v3 compatibility, release-integrity and full-regression jobs so failure notifications identify the affected contract surface;
- upgraded GitHub Actions checkout/setup runtimes to current v7 major releases;
- added package compile, dependency-consistency and executable release-provenance gates;
- added `docs/PRODUCTION_READINESS.md`, explicit incident handling and same-commit green merge requirements;
- updated the README from migration/bootstrap language to the production-live private-leasing scope and fail-closed purchase boundary;
- documented the remaining raw-XLSX distribution and formal GitHub tag/release tasks without weakening the `3.2.1-R` provenance claim.

### Added
- explicit historical source tracks: `REVISION_A`, `RECOVERED_V3_2`, `RECONSTRUCTED_V3_2_1`;
- recovered-v3 household Economics compatibility formulas and pinned candidate fixture values;
- recovered critical-four Confidence and historical tri-state Readiness compatibility functions;
- explicit Revision A weight-coverage vs recovered critical-four close-call strategies;
- offer freshness/status compatibility with separate observed and corrected gate behavior;
- NCAP, family-test and lease-terms composite gate adapters with evidence lineage;
- `3.2.1-R` reconstructed compliance workbook, generated after the exact historical v3.2.1 artifact could not be recovered;
- reconstruction manifest with source/output fingerprints;
- standard-library XLSX validator for the pinned 3.2.1-R fingerprint and PC-07/08/09 formula surfaces.

### Corrected through adversarial review
- **PC-07:** expired ACTIVE offer can no longer pass the corrected offer gate;
- **PC-08:** family Dealbreaker uses `PRØVEKØRSEL` row 25 rather than the Date row 26;
- **PC-09:** acceptable leasing terms require actual/max binding period, minimum price, termination and return evidence;
- non-finite NCAP and lease-term numeric inputs become UNKNOWN rather than silently passing;
- missing derived NCAP components cannot inherit VERIFIED evidence;
- canonical Family/terms gates reject truthy strings such as `"NO"`, `"NEJ"` and `"JA"` where actual booleans are required, preventing Python truthiness from changing eligibility.

### Explicitly unresolved / not claimed
- **PC-01:** Revision A uses evidence-weight coverage at the 95% close-call switch, while recovered v3.2 uses four critical checks; both remain explicit;
- the generated `3.2.1-R` is not claimed to be the missing historical v3.2.1 workbook and does not establish bit-for-bit parity;
- the exact historical v3.2.1 bundled QA harness/output remains unrecovered;
- purchase/new-buy/used-buy economics remain method-blocked pending original P1-P3 findings and purchase anchors;
- byte-safe Git import of the generated XLSX remained a transport task at the time of 0.2.0; D2 in 0.2.1 later retired that distribution path.

## 0.1.0 — 2026-09-03

### Added
- canonical `Vehicle`, `AcquisitionOffer`, `UserProfile`, criteria/evidence and candidate result models;
- deterministic scoring, gates, eligibility, close-call handling and lease economics primitives;
- Floor/Need/Stretch utility with explicit Need utility;
- provenance-bearing direct/derived/modeled evidence semantics;
- source-recovered v3 compatibility controls, including decision-critical gate semantics and historical UNKNOWN-gate ranking behavior;
- explicit profile policy for unused contracted kilometres;
- CI and adversarial falsification suites.

### Corrected through adversarial review
- blocked ineligible candidates from recommendation/close-call promotion;
- connected economics-derived metrics to the canonical criterion pipeline;
- restored Revision A decision numbering and Need=8/10 semantics from recovered originals;
- distinguished non-critical from decision-critical UNKNOWN gates;
- rejected vehicle/offer attribute collisions, unit/type mismatch, cross-currency ranking and invalid economics;
- rejected NaN/infinite numerics, duplicate criterion IDs and zero contracted annual kilometres;
- prevented numeric-string gate values from throwing or silently passing.

### Explicitly not included
- verified v3.2.1 parity;
- first-class historical Confidence and tri-state Readiness adapter;
- resolution of the Revision A vs recovered-v3 close-call coverage conflict;
- complete historical household-cost compatibility adapter;
- offer freshness service;
- production purchase/new-buy/used-buy economics, pending original P1-P3 findings and purchase anchors.
