# Engine 0.2.0 — Known Limitations

**Release boundary:** historical compatibility infrastructure, not historical v3.2.1 proof and not purchase-mode release.

## P1 — Historical v3.2.1 remains unrecovered

The exact historical v3.2.1 workbook/build and bundled QA output were not found. `3.2.1-R` is a generated compliance reconstruction with separate provenance and must not be relabelled as the missing historical artifact.

## P1 — PC-01 close-call authority remains unresolved

Revision A says the 95% threshold switch uses evidence-weight coverage. Recovered v3.2 uses its four critical evidence checks. Engine 0.2.0 represents both explicitly and refuses implicit reconciliation.

## P1 — Purchase modes remain method-blocked

`BUY_NEW` and `BUY_USED` still require the original Acquisition/Purchase P1-P3 findings and purchase Economics Floor/Need/Stretch anchors or an explicit new adjudication. Vehicle utility anchors are not substitutes.

## P2 — Generated XLSX is not yet stored byte-for-byte in Git

The 3.2.1-R workbook was generated and validated in the project environment with SHA-256 `db5d2e8b6429df4229911f6459140ff8d36d8b258609be15a905d4487fc9b972`.

The current GitHub connector corrupted an attempted binary blob. That blob was removed. Git stores the reconstruction manifest, provenance and executable validator; a byte-safe Git/Git-LFS import remains a transport task.

## P2 — Live offer validity remains outside the engine

The compatibility layer can reproduce and validate status/freshness rules, but it does not scrape the live market or guarantee that an offer is current on the day a user evaluates it.

## P2 — External interchange schema remains pre-1.0

Python dataclasses and compatibility functions are the canonical implementation surface. A stable public JSON/CSV schema and migration contract remain future work.

## Allowed release claim

> Engine 0.2.0 adds audited recovered-v3 compatibility infrastructure and a validated 3.2.1-R compliance reconstruction contract.

## Prohibited release claim

> Engine 0.2.0 proves exact historical v3.2.1 parity or provides production-complete lease/new-buy/used-buy decision support.
