# Engine v0.1 — Known Limitations and Deferred Validation

**Status:** explicit release debt, not silent assumptions  
**Applies to:** PR #2 / `build/engine-v0.1`

This document separates what Engine v0.1 now enforces from what cannot yet be claimed because authoritative source artifacts are still missing.

## P1 — Exact v3/v3.2.1 parity is not yet proven

The engine contains primitives for the known Revision A method: label multipliers, Must-have weight + gate, missing-data exclusion, evidence coverage, Floor/Need/Stretch utility, dimensions/subweights/caps, deterministic ranking, close-call bands and readiness blockers.

It does **not** yet prove that a canonical v3.2.1 profile produces identical scores/ranks/gates to the historical workbook. The authoritative v3.2.1 workbook/build and QA fixture must be imported through Issue #1 before parity can be claimed.

**Release consequence:** v0.1 may be merged as the headless engine substrate, but must not be described as a verified drop-in reproduction of v3.2.1.

## P1 — Liquidity guard operational definition is missing

`docs/DECISIONS.md` records that a liquidity guard is part of the established economics treatment. The exact authoritative operational definition/thresholds are not present in the migrated source package.

The engine can represent decision gates and economics-derived criteria, but v0.1 does not invent a liquidity-guard rule.

**Release consequence:** do not claim complete v3 economics parity until the original guard definition is recovered, implemented and falsification-tested.

## P1 — Safety/Family parity is representable, not verified

The engine supports dimensions, editable subweights, Must-have gates and capped weights, which are intended to carry the known Family/safety structure. The precise historical profile configuration — including the authoritative child-protection cap semantics — has not been recovered and tested against v3.2.1.

**Release consequence:** the generic engine substrate is usable, but the canonical Family/safety profile remains pending fixture recovery.

## P1 — Purchase modes remain method-blocked

`BUY_NEW` and `BUY_USED` exist structurally only. Decision-ready purchase economics remain blocked until the original P1–P3 findings and Economics Floor/Need/Stretch anchors are recovered and resolved.

This is deliberate fail-closed behavior, not an implementation defect.

## P1 — Offer freshness/validity is outside v0.1

Evidence can carry `as_of`, but v0.1 does not decide whether an offer is currently active, expired or superseded. Current-market ingestion must therefore validate offer validity before a candidate is presented as current.

**Release consequence:** historical or stale source evidence must not be promoted as a current deal merely because its field-level evidence is VERIFIED.

## P2 — Evidence date is not yet a typed temporal schema

`Evidence.as_of` is currently a string. A future schema version should normalize date/time semantics and define offer validity windows explicitly.

## P2 — External schema/serialization contract is not versioned yet

The Python dataclasses are the current internal canonical model, but a stable JSON/CSV interchange schema and migration/versioning contract have not yet been published.

## P2 — CI action supply-chain hardening

The workflow uses version tags for GitHub Actions rather than immutable commit SHAs. This does not affect decision semantics, but production repository hardening should pin trusted actions and update them deliberately.

## Merge boundary

These limitations do not reopen the resolved P0 findings in PR #2. They do limit the claim that can be made after merge:

> **Allowed claim:** Engine v0.1 is an audited, fail-closed headless substrate implementing the currently recoverable decision semantics.
>
> **Not yet allowed:** Engine v0.1 is a verified bit-for-bit replacement for Leasingmatrix v3.2.1 or a production-complete lease/new-buy/used-buy decision system.
