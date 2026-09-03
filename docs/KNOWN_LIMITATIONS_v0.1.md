# Engine v0.1 — Known Limitations and Deferred Validation

**Status:** explicit release debt after source recovery on 2026-09-03  
**Applies to:** PR #2 / `build/engine-v0.1`

This document separates what Engine v0.1 now enforces from what the recovered originals prove, and from what still cannot be claimed.

## P1 — Exact v3.2.1 parity is not yet proven

A substantial original package is now recovered: v2.1, a later v3 workbook whose internal Change_Log reaches v3.2, Revision A, the v3 implementation handover, and the earlier build/regression/verification scripts.

This closes several previously unknown semantics, but no recovered artifact identifies itself as the later **v3.2.1** build/harness referenced by the final review.

**Release consequence:** v0.1 may be evaluated as a Rev-A-capable headless substrate, but must not be described as a verified drop-in reproduction of v3.2.1.

## P1 — Close-call coverage has a recovered spec/implementation conflict

Exact Revision A D-V3.23 says the 0.20→0.15 threshold switch uses **weight coverage** at the 95% boundary.

The recovered v3/v3.2 workbook instead uses a four-item critical-evidence count (fresh offer, NCAP, insurance quote, family test) for that switch.

The current engine uses evidence-weight coverage, which follows the binding Revision A text. The later v3.2.1 fixture may show whether the workbook implementation was subsequently corrected.

**Release consequence:** keep the conflict explicit; do not claim historical v3.2 parity for close-call coverage semantics.

## P1 — Gate UNKNOWN has two explicitly represented policies

Recovered v3 semantics are:

- gate `FAIL` → ineligible;
- gate `UNKNOWN` remains rank-eligible but makes a decision-critical candidate NOT_READY.

Engine v0.1 can represent this with `unknown_gate_blocks_eligibility=False`. Its generic default remains the stricter fail-closed behavior (`True`) for non-v3 profiles.

**Release consequence:** any v3 compatibility fixture/profile must opt into the recovered policy. Do not call the generic default historical-v3 behavior.

## RECOVERED — Canonical v3 utility and Safety/Family semantics

These are no longer missing for v3/v3.2:

- Need utility = 8/10 = 0.8;
- Range anchors = 200/350/500 km;
- Baggage anchors = 300/profile-need/600 L;
- DC 10–80 anchors = 45/28/18 min, lower is better;
- NCAP gate = at least 5 stars and protocol year at least 2020;
- Family subweights = 30% baggage / 25% by-fit / 30% child-seat-stroller / 15% child protection;
- child-protection gradient = 70%→0 / 95%→10, with UNKNOWN renormalized out of Family.

Exact v3.2.1 parity still requires the later fixture, but these values should no longer be described as unrecovered.

## RECOVERED / REFRAMED — Liquidity was an interim v2.1 score, not a proven v3 gate

The recovered v2.1 workbook establishes the historical liquidity treatment:

- preferred first payment = 30,000 DKK;
- preferred first-12-month cash burden = 85,000 DKK;
- 50/50 blend of threshold fit and relative-to-cheapest 12-month burden.

The full recovered v3 five-dimension architecture does not expose a standalone liquidity dimension or gate.

**Release consequence:** the old limitation “authoritative liquidity guard missing” is retired. Preserve the v2.1 liquidity score as historical behavior; do not invent a v3 liquidity gate unless a later source explicitly reintroduces it.

## P1 — Purchase modes remain method-blocked

`BUY_NEW` and `BUY_USED` exist structurally only. Decision-ready purchase economics remain blocked until the exact Acquisition/Purchase Draft A source, P1–P3 adversarial findings, and **purchase-layer** Economics Floor/Need/Stretch anchors are recovered and resolved.

The vehicle utility anchors recovered above are not purchase economics anchors.

This is deliberate fail-closed behavior, not an implementation defect.

## P1 — Offer freshness/validity is outside v0.1

Evidence can carry `as_of`, but v0.1 does not itself decide whether a live-market offer is active, expired or superseded. The recovered workbook has freshness semantics, but current-market ingestion remains responsible for validating validity before presenting a deal as current.

## P2 — Evidence date is not yet a typed temporal schema

`Evidence.as_of` is currently a string. A future schema version should normalize date/time semantics and define offer validity windows explicitly.

## P2 — External schema/serialization contract is not versioned yet

The Python dataclasses are the current internal canonical model, but a stable JSON/CSV interchange schema and migration/versioning contract have not yet been published.

## P2 — Binary source artifacts are recovered locally but not yet committed

The v2.1 and later v3 workbooks have been recovered in the migration environment and fingerprinted, but the current GitHub connector path does not provide a binary contents upload in this workflow. Exact binary repository import therefore remains pending.

Textual recovery status and hashes are recorded in `docs/RECOVERED_V3_ARTIFACTS_2026-09-03.md`.

## P2 — CI action supply-chain hardening

The workflow uses version tags for GitHub Actions rather than immutable commit SHAs. This does not affect decision semantics, but production repository hardening should pin trusted actions and update them deliberately.

## Merge boundary

The recovery does not justify a v3.2.1 parity claim. It does materially strengthen the substrate and has already falsified and corrected earlier reconstructed assumptions.

> **Allowed claim:** Engine v0.1 is an audited headless substrate that can represent the recovered Revision A/v3 gate semantics and currently recoverable method.
>
> **Not yet allowed:** Engine v0.1 is a verified bit-for-bit replacement for Leasingmatrix v3.2.1 or a production-complete lease/new-buy/used-buy decision system.
