# Engine 0.1.0 — Known Limitations and Deferred Validation

**Status:** explicit release debt after recovered-source adversarial review, 2026-09-03

## P1 — Exact v3.2.1 parity is not proven

Recovered originals include v2.1, a later workbook whose Change_Log reaches v3.2, Revision A, implementation handover and earlier QA scripts. No recovered artifact proves itself to be the final v3.2.1 fixture/harness.

**Consequence:** 0.1.0 may release as an audited substrate; never label it `v3.2.1-parity-verified`.

## P1 — Close-call coverage conflict

Revision A D-V3.23 uses weight coverage at the 95% threshold. The recovered v3/v3.2 workbook uses four critical-evidence checks. Engine 0.1.0 follows binding Revision A. The historical implementation difference remains unresolved until a later authoritative fixture is recovered.

## P1 — First-class Confidence is not yet modeled

Revision A D-V3.25 says non-critical UNKNOWNs reduce Confidence without reducing Readiness. Engine 0.1.0 now correctly prevents non-critical UNKNOWN gates from blocking eligibility/readiness, but it does not expose a first-class Confidence output. A zero-weight gate-only check therefore cannot be represented by weighted evidence coverage alone.

**Consequence:** historical Confidence belongs in the `validation/v3-parity` compatibility layer.

## P1 — Historical tri-state Readiness is not yet modeled

Recovered v3 uses READY / NEARLY READY / NOT READY. Generic 0.1.0 exposes READY / NOT_READY. The parity adapter must recover the exact transition rules, including STALE/EXPIRED effects, without changing the generic core merely for display parity.

## P1 — Historical household Economics adapter is incomplete

Recovered v3 Economics includes lease payment, electricity, insurance, parking, tax/wear reserve and over-km effects. Generic 0.1.0 intentionally provides reusable lease cash/mileage primitives rather than baking household assumptions into core.

The recovered v3 under-use treatment is now representable explicitly with `require_unused_km_value=False`; generic default remains stricter.

## P1 — Offer freshness is not a service yet

Evidence carries `as_of`, but 0.1.0 does not implement ACTIVE/STALE/EXPIRED evaluation or freshness cadence. Recovered workbook semantics should be implemented in ingestion/parity work.

## P1 — Composite historical gates require an adapter

Core gates are atomic attribute/operator/threshold checks with explicit criticality. Historical checks such as NCAP year+stars, family-test state and lease-terms completeness are composite. The preferred approach is to derive auditable attributes with provenance in the compatibility adapter instead of expanding core gate syntax prematurely.

## P1 — Purchase remains method-blocked

`BUY_NEW` and `BUY_USED` are structural only. Exact Purchase Draft A, P1–P3 findings and **purchase-layer** Economics Floor/Need/Stretch anchors remain missing. Vehicle utility anchors recovered from Revision A are not substitutes.

## P2 — External contracts and hardening

- `Evidence.as_of` remains an untyped string.
- stable JSON/CSV serialization and schema migrations are not published.
- CI Actions use version tags instead of immutable SHAs.
- recovered binary v2.1/v3 workbooks are fingerprinted but not yet committed through this connector workflow.

## Recovered values no longer considered missing

- Need utility = 0.8;
- Range 200/350/500 km;
- baggage 300/profile-need/600 L;
- DC 45/28/18 min lower-is-better;
- Family 30/25/30/15;
- child protection 70%→0 / 95%→10;
- NCAP ≥5 stars + protocol year ≥2020;
- v2.1 liquidity thresholds 30,000 DKK / 85,000 DKK and 50/50 blend; this was an interim score, not a recovered v3 liquidity gate.

## Release boundary

> **Allowed:** Engine 0.1.0 is an audited, source-recovery-corrected headless substrate with explicit compatibility controls for recovered Leasingmatrix v3 semantics.
>
> **Not allowed:** Engine 0.1.0 is a verified v3.2.1 replacement or production-complete lease/new-buy/used-buy system.
