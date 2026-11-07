# Release readiness — GLASSBOX-AUTO

**Package represented by this tree: 0.3.0.** The public interface is a bounded
offer-checker beta. It reuses the Engine 0.2.2 economics implementation; historical
scoring and compatibility APIs retain their existing semantics.

## Activation

A feature branch is a release candidate. The beta is available on the release
line only when the reviewed implementation is on `main` and the following checks
pass on that same commit:

| Gate | Required evidence |
|---|---|
| Core engine | Existing scoring, gate, identity, numerical and economics contracts pass |
| Historical compatibility | Recovered-v3 and preserved reconstruction provenance tests pass |
| Public offer interface | Strict transport, confirmation, arithmetic, unknowns, evidence boundaries and adversarial tests pass |
| Package | Wheel and source distribution build; installed CLI works outside the checkout; schemas and synthetic examples are included |
| Runtime matrix | Complete regression passes on Python 3.11, 3.12, 3.13 and 3.14 |
| Separate review | Independent validity and reliability reviews inspect the actual implementation; material findings are fixed and regression-tested |
| User journey | Documented example is actually executed; capability denial is explicit; no invented engine execution or source verification |
| Public contents | No private request, quote, household profile, credential or private workbook is introduced |

Package version or old CI success alone is not release evidence. PR checks can
run on a synthetic merge commit: record that distinction and verify main-push CI
after a merge. New material counterevidence reopens the affected gate.

The exact workflow run and reviewed source revision are recorded in the release
PR. Automated tests and agent walkthroughs are not a human usability study or
certification of all AI providers. See [release scope](RELEASE_0.3.0.md).

## What users can rely on

For the supported constant-payment DKK lease schedule, the checker calculates
from the entered values, preserves unknowns and records the inputs/code identity.
It distinguishes a recurring payment, an average over the full contract,
non-monthly initial cash and a refundable deposit. Extra-mileage arithmetic is
a scenario, not permission to exceed contractual mileage.

Source assertions remain **UNVERIFIED**. A URL, date, hash or human confirmation
does not establish truth. `CALCULATED_FROM_INPUTS`, exit 0 and a within-budget
comparison are not a vehicle recommendation or a claim of affordability.
The complete request must be shown and confirmed in the interaction; its hash
only detects changes. An AI without actual execution capability must say
`UNEXECUTED` and may help prepare inputs or explain the method.

## Scope that stays separate

- The broader generic ranking/agent interface in PR #10 is not completed by this
  narrower contract. Its generic pilot and provider-conformance claims remain open.
- `BUY_NEW` and `BUY_USED` remain method-blocked. Their P1–P3 findings and purchase
  anchors must be recovered or replaced by a separate, source-backed decision.
- PC-01 remains explicit: Revision A weight coverage and recovered-v3 critical
  evidence coverage are different source tracks. The offer checker does not rank
  or run close-call policy and cannot resolve that historical question.
- The engine does not scrape a live catalogue or establish offer availability,
  real-world range, safety, family fit or full ownership cost.
- `3.2.1-R` is historical reconstructed evidence, not byte-identical historical
  v3.2.1. Its public binary distribution was retired on 2026-09-06. Preserve the
  existing manifest and hashes; do not publish the private `3.2.1-RC1` package.
- Ordinary attribution and inspected historical comparisons are accepted under
  [the existing privacy scope](PRIVACY_SCOPE_2026-09-07.md). This does not authorize
  publishing new private profiles or source packages.

## CI failures

Open the failed job and classify the cause: implementation regression,
intended falsifier, source conflict, environment/tooling problem or corrupted
artifact. Fix that cause and retain the regression test. Do not weaken a test
or repeatedly rerun it merely to restore green. A failed package check is a
release blocker even when the arithmetic suite passes.

The underlying engine still follows Revision A: gate `FAIL` is ineligible;
decision-critical `UNKNOWN` can be rank-eligible but never `READY`. A stricter
fail-closed policy remains explicit opt-in. The 0.2.2 inclusive score-gap
round-off allowance and exact 95% coverage switch are unchanged.
