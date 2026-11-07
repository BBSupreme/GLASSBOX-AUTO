# Versioning and Branching Policy

## Version domains

GLASSBOX-AUTO uses **Semantic Versioning** for the headless engine package.

- `0.1.0` = first audited engine substrate release.
- `0.2.0` = historical compatibility/parity infrastructure release: explicit source tracks, recovered v3 adapters, reconstructed 3.2.1-R validation and formula-level regression controls.
- `0.3.0` = bounded public offer-checker beta, reusing the 0.2.2 economics implementation; no generic agent-ranking or provider certification claim.
- `0.x` means the public schema/API may still change as historical parity and purchase support are added.
- A breaking canonical schema/API change before 1.0 increments the minor version.
- Backward-compatible functionality increments minor; backward-compatible fixes increment patch where practical pre-1.0.

Historical workbook labels such as `v2.1`, `v3`, `v3.2`, historical `v3.2.1`, and generated `3.2.1-R` are **source/fixture versions**, not engine SemVer. Never imply equivalence from matching numbers.

## Branch policy

`main` is the only release-line branch and must remain audited and releasable.

Short-lived branches:

- `build/*` — implementation release candidates.
- `validation/*` — parity, fixture, compatibility and independent verification work.
- `fix/*` — narrowly scoped corrections to released behavior.
- `release/*` — integrated public release preparation and verification.
- `data/*` — source/ingestion updates that do not alter decision semantics.
- `research/*` — explicitly non-authoritative experiments.

No long-lived `develop` branch. Long-lived parallel canon is a failure mode for a glass-box project.

## Merge contract

A branch that changes decision semantics merges only through a PR with:

1. source/spec references for the changed rule;
2. falsification tests;
3. green CI on the final head;
4. adversarial review on that same head;
5. explicit unresolved limitations.

Data-only work must preserve provenance and may not silently change scoring, status, gates or ranking semantics.

## Release labels

Current package: `0.3.0`; activation requires the reviewed implementation and all CI gates on the same `main` commit. See `PRODUCTION_READINESS.md`.

Historical compatibility claims must be explicit:

- `recovered-v3-compatible` — source-backed semantics from recovered v3/v3.2 artifacts;
- `v3.2.1-R-reconstructed` — generated compliance reconstruction under Revision A, explicitly not recovered history;
- `v3.2.1-parity-verified` — reserved until an exact historical v3.2.1 fixture/harness proves parity.

The third label remains prohibited.

## Reconstruction rule

When a historical artifact cannot be recovered, a replacement may be generated only if:

- its source artifacts and hashes are recorded;
- assumptions are not silently filled;
- it receives a distinct reconstructed label;
- observed historical behavior and corrected canonical behavior remain distinguishable;
- its fingerprint and validation contract are published;
- later recovery of the historical artifact triggers a fresh parity comparison rather than replacement of provenance.

## Separate purchase scope

Do not fold purchase/new-buy/used-buy economics into historical parity or the public offer-checker release. Purchase implementation should start only after the original Acquisition/Purchase P1-P3 findings and purchase Economics anchors are recovered or re-adjudicated explicitly. This does not block independent leasing-interface work.
