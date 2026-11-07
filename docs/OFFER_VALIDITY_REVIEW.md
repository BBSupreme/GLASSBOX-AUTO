# Offer checker validity review — 2026-11-07

**Disposition: no unresolved P0/P1 validity finding in the reviewed narrow
arithmetic interface.** Integration, package/runtime CI and the separate usability
review still determine release readiness. This is an independent agent review,
not external certification or proof that supplied offers are true/current.

## Scope and evidence

Reviewed `offer_check.py`, `offer_policy.py`, the request/result schemas, the
unchanged canonical `lease_economics` implementation, and
[`OFFER_CHECK_CONTRACT_v1.md`](OFFER_CHECK_CONTRACT_v1.md). The supported claim is
conditional calculation of entered VAT-inclusive private operating-lease terms.
It does not cover vehicle ranking, financial/flexleasing, purchase economics,
contract enforceability, source verification or total ownership cost.

Independent regression file:
[`test_offer_validity_adversarial.py`](../tests/test_offer_validity_adversarial.py).
The separate reviewer authored the test inputs and expected values. Execution on
Python 3.12.14 with pytest 9.1.1: **42 passed, no skips or expected failures**.

Final source/schema verification repeated the same 42 tests successfully against
the installed package's exact `code_fingerprint()` value:
`44bbd1f15d58ebb5fb84268a9d19a6c48ae4145b3baffb2f56156662a48d51dd`.
This binds the independent result to that implementation/schema snapshot; later
code or schema changes require a fresh check. Documentation changes do not enter
that fingerprint.

```bash
python -m pytest -ra tests/test_offer_validity_adversarial.py
```

These checks include fixed historical arithmetic reconciliation against FDM's
published 2024 totals: DKK 241,655, 202,615 and 245,360. They are historical test
oracles, **not available offers or current-market validation**. No provider
conformance or prompt-injection immunity is inferred from these tests.

## Findings and repairs

| Finding | Evidence | Disposition |
|---|---|---|
| Floating sums could falsely exceed an exact budget boundary | 2,656,572.97 + 6,260,967.48 + 1,082,459.55 is exactly DKK 10,000,000, but a binary64 sum is 10,000,000.000000002; a 1e-9 tolerance is insufficient | Fixed: cent-precision input validation and integer-øre budget arithmetic; exact boundary and one-cent-over regressions pass |
| Extreme finite monetary input could escape validation as a decimal exception | `monthly_payment_dkk=1e308` or `1e100` reached decimal remainder evaluation after the maximum-bound failure | Fixed: out-of-range monetary validation stops before precision arithmetic; structured exit-2 rejection is regression tested |
| Initial cash label risked implying complete delivery liquidity | First routine rent and insurance timing were not represented | Resolved by explicit `max_initial_non_monthly_dkk` scope, excluding routine monthly payments; no full day-one liquidity claim |

## What the tests establish

- Mandatory fees contribute once to contract cost; their upfront subset is not
  another fee. Refundable deposits affect initial cash but not payment cost.
- Unknown fees/payment count prevent complete totals; unknown deposit or fee
  timing prevents a positive initial-cash comparison. Insurance uncertainty
  remains unknown when the requested monthly budget includes insurance.
- Equal monthly-payment count and term are required. Unsupported schedules are
  rejected instead of guessed. Boolean, negative, excessive and over-precision
  financial values do not reach calculation.
- Expected excess kilometres are a separate cost scenario. Missing mileage or
  a necessary overage rate remains unknown; unused kilometres do not create an
  invented refund or economic penalty.
- Budget equality is inclusive at cent precision. Comparisons are explicitly
  against entered limits, not affordability findings.
- Future observation dates are rejected. Expiry and source conflict remain
  visible even with complete arithmetic; date-only expiry is not truncated to
  the beginning of its stated day.
- Source URLs/dates never upgrade assertions to `VERIFIED`; recommendation is
  always `NOT_ASSESSED`. Extra asserted evidence-grade fields are rejected.
- A material input/source change invalidates prior confirmation. Confirmation
  and general semantic validation precede blocked purchase dispatch. Duplicate
  IDs, unsupported currency and empty bundles fail explicitly.
- Offer permutation normalizes deterministically without mutating caller input.

## Source-backed interpretation and remaining boundaries

[FDM: 5 farlige leasingfælder](https://fdm.dk/nyheder/nyt-om-trafik-og-biler/2024-10-5-farlige-leasingfaelder-der-kan-koste-dig-kassen)
(17 October 2024; consulted 7 November 2026) explains why initial, recurring,
setup and return charges must be considered together, and why contract length
and mileage matter to comparison. Its dated table supplies the three independent
total-payment test oracles above.

[FDM: Skal du privatlease eller købe?](https://fdm.dk/guides/bilkoeb-leasing-og-salg-af-bil/skal-du-privatlease-eller-koebe)
(17 June 2025; consulted 7 November 2026) distinguishes contracted mileage,
overage charges and contract-dependent under-mileage refunds. A calculated
overage amount therefore cannot establish contractual permission or an optimal
mileage package.

[FDM: Leasingkontrakt](https://fdm.dk/guides/bilkoeb-leasing-og-salg-af-bil/fdm-leasingkontrakt-giver-tryghed)
(21 May 2025; consulted 7 November 2026) separates ordinary lease payments from
insurance and owner tax. This supports labeling the checker as entered lease
payment arithmetic rather than complete car cost.

The interface cannot detect an omitted fee, a falsely described VAT basis,
misidentified vehicle/quote, unsupported contract condition, or incorrect source
assertion merely from syntactically valid JSON. The user-facing confirmation must
show these assumptions; source and contract checks remain necessary. Current
offer availability, suitability and provider compatibility require their own
evidence and are not approved by this review.
