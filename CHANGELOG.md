# Changelog

All notable engine changes are documented here. Historical workbook version labels are tracked separately from package Semantic Versioning.

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
- production purchase/new-buy/used-buy economics, pending original P1–P3 findings and purchase anchors.
