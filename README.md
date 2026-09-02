# GLASSBOX-AUTO

**Open, auditable decision support for car acquisition: private leasing, new purchase, and used purchase.**

GLASSBOX-AUTO is the public home of the Leasingmatrix 2026 project. The goal is not to produce a black-box “best car” score. The goal is to make the assumptions, evidence, economics, weighting, gates, uncertainty, and decision logic inspectable — and challengeable.

## Status

**Repository bootstrap: 2026-09-02**

The project is being migrated from a working ChatGPT/Excel research project into an open repository. The architecture and decision method are more mature than the repository itself. Some previously reviewed artifacts are not yet physically available in this repo and are explicitly tracked as pending imports rather than reconstructed from memory.

## What this project covers

- Private leasing offers
- New-car purchase
- Used-car purchase
- User-specific decision criteria and editable weights
- Must-have decision gates
- Evidence quality and readiness
- Economic comparison across acquisition modes
- Mileage-fit and stress testing
- Residual-value scenarios and break-even analysis
- QA and reproducibility

## Core principle: glass box, not black box

Every recommendation should be traceable to:

1. **Source evidence** — where the number or claim came from.
2. **Normalization** — how unlike offers were made comparable.
3. **Assumptions** — what had to be estimated or inferred.
4. **Decision logic** — weights, gates, utility curves, scenario rules.
5. **Uncertainty** — what is verified, estimated, missing, or decision-critical.
6. **Output** — why one candidate ranks above another.

The method should be open to adversarial review. A conclusion that cannot survive inspection should not be promoted as a decision.

## Repository map

```text
.
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── docs/
│   ├── PROJECT_CHARTER.md
│   ├── METHOD.md
│   ├── DECISIONS.md
│   ├── VERSION_HISTORY.md
│   ├── QA_AND_VALIDATION.md
│   ├── ACQUISITION_PURCHASE_LAYER.md
│   └── MIGRATION_MANIFEST.md
├── data/
│   └── source-material/
├── models/
│   └── legacy/
└── qa/
```

## Current canonical decisions

The current method inherits the Leasingmatrix 2026 v3 line and its binding Revision A decisions. Among the decisions already locked:

- **Must-have** is both a very-high weight and a decision-critical gate.
- Missing data is not silently scored as zero; normalized weighting excludes missing data, while readiness and coverage expose the gap.
- Safety is handled as a gate plus capped child-protection evidence inside Family, not as an independent free-floating weight.
- Diminishing utility uses fixed piecewise-linear **Floor / Need / Stretch** anchors.
- Readiness is driven by decision-critical unknowns and close-call state.
- Modeled real-world range is **ESTIMATED**; **VERIFIED** requires matched measurement evidence.
- Close-call thresholds are stricter when evidence coverage is high.
- QA must include formula/mapping checks, deterministic ties, utility curves, frontend hard-code scanning, and Excel/LibreOffice compatibility.

See [`docs/DECISIONS.md`](docs/DECISIONS.md) and [`docs/METHOD.md`](docs/METHOD.md).

## Acquisition modes

The architecture separates three concepts:

- **Vehicle** — the underlying car/configuration.
- **Acquisition_Offer** — a specific lease, new-purchase, or used-purchase offer.
- **Decision_Candidate** — the comparable object used by the decision engine.

Supported conceptual modes are:

- `LEASE_NEW`
- `BUY_NEW`
- `BUY_USED`

Purchase economics must not treat loan principal as an economic cost. Cash flow, financing, equity/residual value, and economic cost are separate views.

The acquisition/purchase extension is architecturally approved but its implementation remains gated by unresolved method items documented in [`docs/ACQUISITION_PURCHASE_LAYER.md`](docs/ACQUISITION_PURCHASE_LAYER.md).

## Open-source posture

This repository starts public by design. Contributions are welcome when they improve transparency, evidence quality, model correctness, or reproducibility. Manufacturer marketing claims, dealer offers, journalistic tests, user reports, and modeled estimates should not be treated as equivalent evidence.

## Important limitation during migration

The repository currently contains only source artifacts that are actually available during this migration. Previously referenced workbooks, scripts, review documents, and QA outputs are listed in the migration manifest as **pending import** until their exact bytes are available. They are not recreated from memory and presented as originals.

## Disclaimer

This project is decision-support, not financial, legal, tax, insurance, or automotive safety advice. Pricing, taxation, incentives, specifications, and offers can change. Always verify decision-critical facts against current primary sources before acting.
