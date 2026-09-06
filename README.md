# GLASSBOX-AUTO

[![engine-ci](https://github.com/BBSupreme/GLASSBOX-AUTO/actions/workflows/engine-ci.yml/badge.svg?branch=main)](https://github.com/BBSupreme/GLASSBOX-AUTO/actions/workflows/engine-ci.yml)

**Open, auditable decision support for car acquisition.**

GLASSBOX-AUTO is the public home of the Leasingmatrix 2026 method and decision engine. The goal is not a black-box “best car” score. The goal is to make assumptions, evidence, economics, weighting, gates, uncertainty and recommendation logic inspectable and falsifiable.

## Status

**Engine release line: 0.2.x**

The current production baseline is **Engine 0.2.0** on `main` at the reviewed go-live commit. The **0.2.1 candidate** corrects the canonical decision-critical gate default so it matches binding Revision A: gate `FAIL` is ineligible; decision-critical gate `UNKNOWN` may remain rank-eligible but is always `NOT_READY`. Callers that deliberately need a stricter fail-closed ranking policy can request it explicitly.

A candidate is not production-live merely because its branch is green. It becomes live only after the reviewed implementation is on `main` and the repository's same-commit go-live gates pass.

`BUY_NEW` and `BUY_USED` are architectural modes but are **not production-enabled economics modes**. They remain fail-closed until the original acquisition/purchase P1-P3 findings and purchase Economics anchors are recovered or replaced by an explicit source-backed method decision.

See [`docs/PRODUCTION_READINESS.md`](docs/PRODUCTION_READINESS.md), [`docs/RELEASE_0.2.0.md`](docs/RELEASE_0.2.0.md), [`docs/RELEASE_0.2.1.md`](docs/RELEASE_0.2.1.md) and [`docs/KNOWN_LIMITATIONS_v0.2.md`](docs/KNOWN_LIMITATIONS_v0.2.md).

## What the 0.2.x engine provides

- deterministic Python decision engine for private leasing;
- user-specific criteria, editable weights and Must-have gates;
- Floor / Need / Stretch utility curves;
- evidence grades, provenance, coverage and readiness controls;
- lease economics, mileage scenarios and stress testing;
- recovered-v3 compatibility adapters for Confidence, Readiness, offer freshness and composite gates;
- explicit Revision A vs recovered-v3 source-track differences rather than silent reconciliation;
- `3.2.1-R` reconstruction manifest and executable workbook validator as historical provenance/compatibility evidence;
- adversarial regression suite and classified CI release gates.

## What is not production scope

- new-car and used-car purchase economics;
- automatic live-market scraping/freshness service;
- a claim of byte-identical historical v3.2.1 recovery;
- public distribution of the `3.2.1-R` reconstructed XLSX. That binary import was retired on 2026-09-06; its pinned provenance record remains.

## Core principle: glass box, not black box

Every recommendation should be traceable to:

1. **Source evidence** — where the number or claim came from.
2. **Normalization** — how unlike offers were made comparable.
3. **Assumptions** — what had to be estimated or inferred.
4. **Decision logic** — weights, gates, utility curves and scenario rules.
5. **Uncertainty** — what is verified, estimated, missing or decision-critical.
6. **Output** — why one candidate ranks above another.

A conclusion that cannot survive adversarial inspection should not be promoted as decision-ready.

## Repository map

```text
.
├── README.md
├── CHANGELOG.md
├── LICENSE
├── CONTRIBUTING.md
├── pyproject.toml
├── .github/workflows/
│   └── engine-ci.yml
├── docs/
│   ├── PROJECT_CHARTER.md
│   ├── METHOD.md
│   ├── DECISIONS.md
│   ├── QA_AND_VALIDATION.md
│   ├── PRODUCTION_READINESS.md
│   ├── RELEASE_0.2.0.md
│   ├── RELEASE_0.2.1.md
│   ├── ACQUISITION_PURCHASE_LAYER.md
│   └── MIGRATION_MANIFEST.md
├── fixtures/
│   └── v3/
├── src/
│   └── glassbox_auto/
└── tests/
```

## Canonical method decisions

The current method inherits the Leasingmatrix 2026 v3 line and binding Revision A decisions. Among the locked rules:

- **Must-have** is both a very-high weight and a decision-critical gate.
- Missing data is not silently scored as zero; scoring excludes unavailable values while coverage/readiness expose the gap.
- Gate `FAIL` is ineligible; decision-critical `UNKNOWN` may remain ranked but cannot be READY.
- Safety is a gate plus capped child-protection evidence inside Family, not an independent free-floating weight.
- Diminishing utility uses fixed piecewise-linear **Floor / Need / Stretch** anchors.
- Readiness is driven by decision-critical uncertainty and close-call state.
- Modeled real-world range is **ESTIMATED**; **VERIFIED** requires matched measurement evidence.
- Close-call thresholds are stricter when the applicable evidence-coverage rule is high.
- Historical source conflicts are represented explicitly rather than resolved by whichever behavior reproduces a desired ranking.

See [`docs/DECISIONS.md`](docs/DECISIONS.md) and [`docs/METHOD.md`](docs/METHOD.md).

## Acquisition architecture

The model separates:

- **Vehicle** — the underlying car/configuration.
- **AcquisitionOffer** — a specific lease/new-buy/used-buy offer.
- **DecisionCandidate** — the comparable object used by the engine.

Modes are:

- `LEASE_NEW` — production-supported in the 0.2.x release line;
- `BUY_NEW` — fail-closed pending method completion;
- `BUY_USED` — fail-closed pending method completion.

Purchase economics must not treat loan principal as economic cost. Cash flow, financing, equity/residual value and economic cost remain separate views.

## CI and incident handling

`engine-ci` deliberately separates failures into:

- **contracts / core engine**;
- **contracts / recovered v3 compatibility**;
- **release / integrity and package smoke**;
- **regression / full suite**.

A failed run is evidence to investigate, not a nuisance to re-run away. The incident process is documented in [`docs/PRODUCTION_READINESS.md`](docs/PRODUCTION_READINESS.md).

## Open-source posture

This repository is public by design. Contributions are welcome when they improve transparency, evidence quality, correctness or reproducibility. Manufacturer marketing claims, dealer offers, journalistic tests, user reports and modeled estimates must not be treated as equivalent evidence.

## Artifact provenance

`3.2.1-R` is explicitly a **reconstructed compliance artifact**, not the recovered historical v3.2.1 workbook. Its manifest pins source and output hashes and forbids silently upgrading the historical parity claim. Its public binary import is retired; the provenance record and validator remain. See [`docs/V3_2_1_RECONSTRUCTION_2026-09-03.md`](docs/V3_2_1_RECONSTRUCTION_2026-09-03.md).

The separate private `3.2.1-RC1` workbook review track has its own lineage and release gates. It must not be treated as an Engine release artifact.

## Disclaimer

This project is decision support, not financial, legal, tax, insurance or automotive safety advice. Pricing, taxation, incentives, specifications and offers can change. Verify decision-critical facts against current primary sources before acting.
