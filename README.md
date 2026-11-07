# GLASSBOX-AUTO

[![engine-ci](https://github.com/BBSupreme/GLASSBOX-AUTO/actions/workflows/engine-ci.yml/badge.svg?branch=main)](https://github.com/BBSupreme/GLASSBOX-AUTO/actions/workflows/engine-ci.yml)

**Check the costs and missing terms in a private-leasing offer, with an AI assistant and an open Python engine.**

[Dansk: start her](docs/QUICKSTART_DA.md) · [AI and command-line guide](docs/AI_QUICKSTART.md) · [Input contract](docs/OFFER_CHECK_CONTRACT_v1.md) · [Method](docs/METHOD.md)

Give your assistant dated offers and your expected mileage. It prepares reviewable inputs, asks you to confirm them, runs the engine, and explains the result. You can inspect the inputs, formulas and code behind every calculation.

The input contract covers Danish private operating leases for new cars, with VAT-inclusive DKK prices and constant monthly payments. Used-car leasing, business/ex-VAT offers, financial/flexleasing and residual-value obligations are outside this beta.

**Status: public offer-checker beta.** A feature branch is a release candidate; the release is active only when the reviewed implementation and all passing checks are on the exact `main` commit. A green badge for an older commit is insufficient. See [production readiness](docs/PRODUCTION_READINESS.md).

## What you get

| The checker shows | What the result does not establish |
|---|---|
| Lease payments over the full term and their monthly average | The entire cost of running the car |
| Recurring payment and initial non-monthly cash separately | That a low advertised payment makes the car affordable |
| Flat extra-kilometre charge scenarios, with the required inputs | That the contract permits your intended mileage |
| Missing values, source dates and stated offer expiry | That the source is correct or the offer is available |
| Calculations for the offers you supply | A best-car ranking, market search, or purchase-versus-lease advice |

Unknown amounts stay unknown. A refundable deposit affects cash required but is kept outside the nonrefundable lease total. Different durations and mileage allowances remain visible. The evaluator does not fetch URLs, authenticate quotes or certify vehicle suitability.

## Start with an AI assistant

The assistant needs these files **and the ability to run Python**. Reading this GitHub page alone is not enough. Copy this prompt into a capable assistant:

```text
Use GLASSBOX-AUTO to check my private-leasing offers:
https://github.com/BBSupreme/GLASSBOX-AUTO

Read AGENTS.md and docs/AI_QUICKSTART.md from the same pinned commit.
First check whether you can actually read the files and run the Python CLI.
If you cannot, say UNEXECUTED and help me prepare the inputs instead.

Ask for my offers, expected annual mileage and any budget limits. Preserve
missing terms as unknown. Show me the complete prepared inputs, sources,
dates and assumptions before asking for confirmation. After I confirm,
execute the checker and explain its output, with the command, version,
request fingerprint and result fingerprint. Do not substitute your own
ranking or claim that supplied offer details have been verified.
```

Use the [Danish prompt and intake guide](docs/QUICKSTART_DA.md) if you prefer. An assistant without execution tools can help read a quote and identify unanswered questions; it must label that work **UNEXECUTED**.

## Run a synthetic example locally

Requires Python 3.11 or newer. The examples contain fictional offers, not current deals.

```bash
git clone https://github.com/BBSupreme/GLASSBOX-AUTO.git
cd GLASSBOX-AUTO
python -m venv .venv
```

Activate with `source .venv/bin/activate` on macOS/Linux or `.venv\Scripts\Activate.ps1` in Windows PowerShell, then:

```bash
python -m pip install .
python -m glassbox_auto.cli --version
python -m glassbox_auto.cli example
python -m glassbox_auto.cli prepare src/glassbox_auto/examples/complete.json
```

Continue with the [complete example walkthrough](docs/AI_QUICKSTART.md#try-the-synthetic-example) to confirm the inputs and run the assessment. Keep a record of `git rev-parse HEAD`; use the same commit for the schema, executable and instructions.

The CLI has two steps:

```bash
python -m glassbox_auto.cli prepare request.json
python -m glassbox_auto.cli assess confirmed-request.json --output result.json
```

`prepare` validates and displays the request. `assess` requires the current request fingerprint recorded after confirmation. The safe `--output` writer requires POSIX filesystem primitives and never overwrites a file; on other systems omit `--output` and read JSON from stdout. A zero exit code means calculation completed; it is not approval to sign a lease.

## Read the result correctly

Start with missing terms and source limitations. Keep duration and mileage alongside each price. An average monthly payment spreads the nonrefundable initial payment and fees across the term; it differs from the bill due each month.

The `max_initial_non_monthly_dkk` check covers the initial payment, fees due initially and refundable deposit. **It excludes the first regular monthly instalment.** Add that instalment separately when planning day-one cash. The monthly limit checks the recurring lease payment, with incremental insurance only if you selected that basis. Neither limit is a complete affordability assessment.

All supplied source details remain unverified assertions. A URL, recent date, hash and your confirmation improve traceability; none proves the quote true. Recheck material terms with the provider. No named AI-provider compatibility is claimed; actual file and process capabilities determine whether a run is possible.

## Report a problem

[Open an issue](https://github.com/BBSupreme/GLASSBOX-AUTO/issues/new/choose) with the commit, Python version, exact command, observed result and expected result. A small synthetic reproducer is best. Remove names, addresses, account numbers, quote identifiers and other private details before sharing. The evaluator does not upload requests or results; your AI host has its own handling of anything you give it.

See [CONTRIBUTING.md](CONTRIBUTING.md) for development and validation. The schemas are versioned; beta status is not a promise of compatibility with future versions.

## Engine, method and historical work

The underlying engine also contains criteria, weights, Must-have gates, Floor / Need / Stretch utility curves, evidence coverage, close-call controls and recovered-v3 compatibility adapters. These lower-level capabilities are broader than the public offer check. The beta does not invent preferences or utility anchors, or turn a cost comparison into an overall vehicle ranking.

Binding Revision A rules remain in [DECISIONS.md](docs/DECISIONS.md) and [METHOD.md](docs/METHOD.md). Gate `FAIL` is ineligible; decision-critical `UNKNOWN` may remain rank-eligible but is always `NOT_READY`. Modeled real-world range is `ESTIMATED`; `VERIFIED` requires matched measurement. The unresolved PC-01 coverage-authority distinction remains explicit.

`BUY_NEW` and `BUY_USED` remain method-blocked. Purchase economics needs its own source-backed method and release. The broader agent-ranking design in [PR #10](https://github.com/BBSupreme/GLASSBOX-AUTO/pull/10) is separate from this narrower contract.

`3.2.1-R` is historical reconstruction evidence, not a recovered byte-identical workbook. Its public XLSX distribution was retired; its manifest and validator remain. The private `3.2.1-RC1` workbook track is not an Engine release artifact. See [provenance](docs/V3_2_1_RECONSTRUCTION_2026-09-03.md) and [privacy scope](docs/PRIVACY_SCOPE_2026-09-07.md).

Earlier fixes and limitations are recorded in [0.2.2 release notes](docs/RELEASE_0.2.2.md), [repair changelog](docs/REPAIR_CHANGELOG_0.2.2.md), [known limitations](docs/KNOWN_LIMITATIONS_v0.2.md) and [CHANGELOG.md](CHANGELOG.md). Code uses [Apache-2.0](LICENSE); third-party source materials retain their original ownership.

This is decision support. It does not replace current contract, financial, tax, insurance or safety advice.
