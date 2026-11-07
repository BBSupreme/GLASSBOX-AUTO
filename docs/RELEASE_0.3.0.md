# 0.3.0 — public offer-checker beta

Prepared 2026-11-07 from Engine 0.2.2, main baseline
`61201f9e9a00e5bd0fdf59c530bfd502d330265e`.

## What changed

Reddit readers now have a bounded way to give an AI their lease inputs and ask
it to execute the same inspectable calculation. The entry points are the
[Danish quickstart](QUICKSTART_DA.md), [AI guide](AI_QUICKSTART.md), and
[agent instructions](../AGENTS.md).

The versioned [offer-check contract](OFFER_CHECK_CONTRACT_v1.md) covers new-car
private leasing in DKK with constant monthly payments over the full entered term.
It adds closed schemas, full-request confirmation, an offline CLI, deterministic
digests, bounded execution and no-overwrite output publication. Calculations use
the existing engine, with no changes to its scoring, ranking or historical
compatibility semantics.

Inputs and results distinguish unknown fees from zero fees, refundable deposits
from cost, insurance from lease rent, initial non-monthly cash from first-month
cash planning, and excess-mileage scenarios from contract permission. Evidence
stays unverified, even with a plausible URL, dates and complete traceability.

## Supported claim

> An open-source beta that calculates the entered costs of supported Danish
> private-leasing offers and exposes missing inputs and assumptions. An AI can
> guide the process if it can read the files and actually run Python.

No market-wide best-deal, best-car, source-verification, purchase, human-usability
or cross-provider certification claim is made. Read-only models can help prepare
the request but must report `UNEXECUTED`.

## Relation to earlier agent specifications

PR #10 proposed a generic decision/ranking interface with evidence policies,
criteria, vehicles, offers and a twelve-execution pilot. That contract has not
been represented as accepted or implemented by this release. The public
offer-checker is a deliberately smaller, independently reviewed contract. It
retains the relevant protections: common validation before method dispatch,
deterministic decision versus raw transport hashes, truthful execution status,
complete-input confirmation and untrusted source text.

The narrow walkthrough and adversarial tests prove only their recorded cases.
They do not silently satisfy the earlier generic pilot or named-provider gates.

## Verification and activation

The release PR records the source commit, independent findings and their fixes,
test counts and clean-wheel execution. `engine-ci` runs the complete suite on
Python 3.11–3.14 and exercises the installed CLI outside the source checkout.
The checked-in tests remain reproducible with `pytest`; the wheel workflow is
reproducible with `python -m build` and `scripts/smoke_offer_checker.py`.

This tree is a candidate until the reviewed implementation is on `main` and all
same-commit [release gates](PRODUCTION_READINESS.md) pass. Neither this release
note nor a successful older workflow is evidence that those events occurred.

## Remaining limits

- Constant payment schedule only; no early-exit, tiered mileage or purchase model.
- No guessed under-mileage refund and no automatic currency conversion.
- Source availability, conflicts and correctness need external resolution.
- Budget comparisons cover the explicitly selected components, not full car ownership.
- Python JSON determinism is tested across the declared runtimes; no RFC 8785 claim.
- Provider compatibility depends on actual execution capability, not a model name.
- PC-01 and the private workbook release remain separate and unresolved.

For the economic interpretation, see FDM's [leasing pitfalls](https://fdm.dk/nyheder/nyt-om-trafik-og-biler/2024-10-5-farlige-leasingfaelder-der-kan-koste-dig-kassen)
and [private-leasing contract guide](https://fdm.dk/guides/bilkoeb-leasing-og-salg-af-bil/fdm-leasingkontrakt-giver-tryghed).
These sources motivate checking fees, contract terms and excluded running costs;
they do not endorse or validate this software.
