# Changelog

All notable engine changes are documented here. Historical workbook version labels are tracked separately from package Semantic Versioning.

## 0.2.0 — 2026-09-03

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
- byte-safe Git import of the generated XLSX remains a transport task; a corrupt connector upload was removed rather than accepted.

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
