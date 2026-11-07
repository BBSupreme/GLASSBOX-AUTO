# Public offer checker v1 contract

Status: implementation contract for the narrow public beta, 2026-11-07.

This interface assesses entered Danish new-car private-leasing payment schedules.
It does not implement the generic scoring/agent design in PR #10. In particular it
never emits READY, an overall ranking, verified source claims, or a recommendation.
The historical engine and broader agent specification keep their existing scope.
The narrow contract below owns this interface's wire and economic semantics.

## Request

`schema_version` is `offer-check-request.v1`; `policy_id` is
`dk-private-lease.v1`; `assessment_at` is a valid exact UTC
`YYYY-MM-DDTHH:MM:SSZ` timestamp. No implicit current clock is used.

```json
{
  "schema_version": "offer-check-request.v1",
  "policy_id": "dk-private-lease.v1",
  "assessment_at": "2026-11-07T10:00:00Z",
  "profile": {
    "expected_annual_km": 15000,
    "max_initial_non_monthly_dkk": 20000,
    "max_monthly_dkk": 5000,
    "monthly_budget_basis": "LEASE_AND_INSURANCE"
  },
  "confirmation": null,
  "offers": [{
    "offer_id": "synthetic-a",
    "vehicle": "Synthetic family EV A",
    "mode": "LEASE_NEW",
    "currency": "DKK",
    "source": {
      "kind": "SYNTHETIC",
      "locator": "Synthetic example; not an available market offer",
      "url": null,
      "observed_on": "2026-11-07",
      "valid_until": null,
      "conflict": false
    },
    "term_months": 36,
    "monthly_payment_count": 36,
    "annual_km": 15000,
    "upfront_payment_dkk": 15000,
    "monthly_payment_dkk": 3500,
    "mandatory_fees_dkk": 600,
    "fees_upfront_dkk": 0,
    "refundable_deposit_dkk": 0,
    "monthly_insurance_dkk": 500,
    "overage_dkk_per_km": 1.5
  }]
}
```

All shown fields except `confirmation` are required; the amounts, kilometre
values, term/payment-count fields and budget limits allow `null` for unknown.
`monthly_budget_basis` must explicitly be `LEASE_ONLY` or `LEASE_AND_INSURANCE`.
The source locator is a short human-readable citation, such as a written quote's
date/reference; it must not contain private contact/account details. It may be
null. The URL may be null or an absolute HTTP(S) URL, without credentials. The
checker does not fetch it. Unknown fields, including asserted evidence grades,
commands, scoring weights, and extra policies, are rejected.

`confirmation` is either absent/null for `prepare`, or exactly
`{"request_sha256":"<64 lowercase hex characters>"}` for `assess`. The digest
covers the entire validated normalized request with `confirmation` removed:
profile, offers, source assertions, dates, and policy. It detects changed inputs;
it does **not** authenticate user assent. The AI must show the assumptions and
retain the user's actual confirmation before inserting the hash. Any material
change requires a new prepare/confirmation cycle. Offer arrays normalize by
unique `offer_id`; every other sequence retains its order. Do not invent unknowns.

## Monetary and schedule meaning

All prices are consumer amounts including VAT for private operational leases,
with no residual-value liability. Business/ex-VAT quotes, flexleasing, used leases
and residual-value guarantees are outside this interface. The agent must confirm
this scope at intake; the calculator cannot infer it from numbers. All money is
DKK; no currency conversion is implemented. Amounts are finite,
nonnegative numbers. Fixed monetary fields/budget caps permit at most two decimal
places; per-kilometre charges permit at most six. Term and payment count are
positive integer JSON tokens up to 120 (`36`, not `36.0`); annual km values are integers between 0 and 200,000
(contracted annual km must be positive); monetary amounts are capped at 10 million
DKK. These are interface resource/domain bounds, not recommended user settings.

- `upfront_payment_dkk` is a **nonrefundable** initial payment in addition to all
  recurring payments. Do not enter a headline initial payment that includes the
  first regular payment without separating it from that regular payment.
- `monthly_payment_dkk` is the constant contractual payment, including any
  recurring mandatory charges. There are exactly `monthly_payment_count` such
  payments. Known count must equal known `term_months`; irregular schedules are
  unsupported and rejected instead of double-counted. If count is unknown, the
  total remains unknown. A count of term minus one is not silently normalized.
- `mandatory_fees_dkk` is the total additional nonrefundable compulsory fees over
  the entire contract, excluding the initial and recurring payments. Include
  known compulsory delivery/return fees exactly once. Unknown fees are `null`.
- `fees_upfront_dkk` is the part of those fees due initially, not an extra charge.
  It cannot exceed known mandatory fees. Null timing keeps initial outlay unknown.
- `refundable_deposit_dkk` is excluded from economic payment totals but included
  in initial non-monthly cash requirements. Return is conditional, not guaranteed.
- `monthly_insurance_dkk` is an incremental insurance cost, excluding any already
  included in the lease payment. Use zero only when there is no incremental cost.
- `overage_dkk_per_km` is a flat extra-km rate. Tiered/capped rates are outside this
  contract. A calculated charge does not prove that the lease permits that mileage.

`max_initial_non_monthly_dkk` limits **initial non-monthly cash**: initial payment + upfront
fees + refundable deposit. It excludes the first routine monthly instalment; show
this definition prominently and add that instalment separately for day-one cash
planning. `max_monthly_dkk` limits recurring lease payment, plus incremental
insurance only under `LEASE_AND_INSURANCE`. It excludes amortized upfront money,
energy/fuel, taxes paid separately, tyres, optional services, damage and other
ownership costs. It is not a total-cost-of-ownership budget.

## Computation and interpretation

The existing `lease_economics` implementation owns contract cash and flat excess
mileage arithmetic. Annual kilometre allowances and expected usage are prorated
as annual km × term months / 12. A contract with a different total allowance must
not be silently annualized to fit this model; obtain equivalent terms first.
The adapter sets `require_unused_km_value=False`, explicitly:
under-use has no assumed refund or invented economic penalty. Base contract
payment = initial + count × monthly + compulsory fees. Deposit and incremental
insurance are kept separate. Average contract payment divides base by term; it
must never be called the recurring payment. Expected-mileage total adds the flat
extra-km scenario only when computable; no under-mileage refund is inferred.
Missing schedule or fee inputs never become zero. Decimal display rounding must
not change deterministic payloads. Budget components and limits are converted to integer øre from their entered
decimal values before addition/comparison, so binary-float noise cannot change a
cent-exact budget outcome.

Offers retain identifier order, not cost/rank order. No cross-offer winner is
computed; different terms and missing values can make an average misleading.
Budget outcomes are `WITHIN_ENTERED_LIMIT`, `EXCEEDS_ENTERED_LIMIT`, `UNKNOWN`, or
`NOT_REQUESTED`; these are comparisons of entered numbers, not affordability or
eligibility decisions. Complete arithmetic yields `CALCULATED_FROM_INPUTS`;
missing required arithmetic yields `INCOMPLETE_INPUTS`. All outputs have
`source_verification: UNVERIFIED` and `recommendation: NOT_ASSESSED`.

Sources are `SYNTHETIC` or `USER_SUPPLIED`. URL/date/locator do not certify a claim.
The checker reports observed age, missing source/date, expiry, conflicts, and the
need to confirm terms. There is deliberately no invented freshness cutoff.
Future observation dates are invalid; an expired offer may be calculated as a
historical example and is visibly flagged. Source conflicts stay unresolved.
Vehicle suitability, range, safety, availability, early termination, damage,
contract conditions and source truth need external checks and are not scored.

## Validation and deterministic result

General structure, common types/dates, IDs, source shapes, numeric bounds and
confirmation integrity are checked before method dispatch. Recognized purchases
(`BUY_NEW`, `BUY_USED`) then fail with exit 3; they do not require invented lease
fields. Unknown modes and malformed requests fail with exit 2. Lease structural
checks follow; currencies other than DKK fail with exit 6; empty offers fail with
exit 5. Calculation/invariant errors use exit 4. Successful calculation has exit
0 even when inputs are incomplete or a budget is exceeded.

`validate_request(request, require_confirmation=True)` returns a copied normalized
request. `request_fingerprint(request)` hashes that normalized request excluding
confirmation. `evaluate_request(request)` validates then returns the deterministic
`decision` object. `OfferCheckError` carries `exit_code`, `code`, and lexical
`paths`; errors never echo entered values. Transport parsing and bounded execution
are owned by `wire.py` and the CLI. Package-local JSON schemas describe the same
closed request/result shapes; semantic cross-field checks remain in Python.

The CLI emits `{decision, decision_payload_sha256, transport}`. Transport includes
the raw input hash; raw bytes, paths and moving runtime metadata never enter the
decision. Decision contains schema/policy/package identities, code fingerprint,
assessment_at, normalized-request and profile fingerprints, the checked inputs,
results and limitations. `GBX-PYJSON-1` uses UTF-8, sorted keys, no whitespace,
finite native Python JSON numbers, positive float zero, preserved Unicode, and
no trailing newline; numeric `1` and `1.0` remain distinct. This is Python JSON
conformance, not an RFC 8785 claim. Wire validation rejects duplicate keys,
nonfinite values, invalid Unicode, oversized strings/trees and unsafe integers.

References: [Python JSON](https://docs.python.org/3/library/json.html),
[JSON Schema 2020-12](https://json-schema.org/draft/2020-12),
[existing engine economics](../src/glassbox_auto/economics.py).
