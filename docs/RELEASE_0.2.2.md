# Engine 0.2.2 — readiness-integrity repair

Prepared: 2026-09-07. Status: candidate until separately reviewed, merged and green on the exact resulting main commit. A tag or package version is not proof of activation.

## Scope

Repair the three reproduced engine defects from PR #10 / issues #11–#13. Preserve the binding Revision A gate boundary introduced in 0.2.1. The numerical repair source was prepared at `f5af1746323f01d0efc664c3b2b8f63190a3bfc3`; subsequent release-identity changes require their own exact-head CI and review. Actual reviewer responses and run IDs are recorded on PR #14.

## Corrections

- Inclusive close-call score-gap comparisons use the ordinary `gap <= threshold` check plus an absolute tolerance of 1e-12 score points with zero relative tolerance. This accommodates round-off at 0.15/0.20 without rounding displayed scores into ranking policy. The documented tolerance includes a tiny allowance above the nominal band; wider gaps must remain outside. The coverage switch at 0.95 and PC-01 source-track authority are unchanged.
- Candidate IDs encode each raw vehicle/offer component separately before joining. Duplicate serialized IDs and duplicate raw pairs are rejected before ranking.
- Non-finite effective weights, aggregates, utility spans, economic values and result leaves raise explicit errors; successful candidate score and coverage ranges are checked. No NaN/Infinity READY result is accepted.
- Scoring aggregates use consistent finite summation, and the weighted mean is divided before multiplication by ten. This avoids the ordinary-weight regression caught during builder self-review.

## Compatibility

Plain unreserved IDs such as `car-1:offer_2` are unchanged. Reserved characters are escaped: raw pair (`a:b`, `c`) produces `a%3Ab:c`; (`a`, `b:c`) produces `a:b%3Ac`. Rebuild persisted affected IDs from the original component fields, not by splitting an ambiguous legacy string. Raw vehicle_id and offer_id remain in each result.

Numeric inputs whose intermediate calculations cannot be represented safely may now raise NumericalIntegrityError, a ValueError subtype. This is a deliberate failure instead of a corrupt result. The engine is not arbitrary-precision arithmetic. Do not clamp, fabricate UNKNOWN evidence or drop criteria to bypass an error.

## Required verification

Core contracts, recovered-v3 compatibility, wheel/version/provenance checks and full regression on Python 3.11, 3.12, 3.13 and 3.14 must pass. The original 27 review falsifiers remain in the repository without xfail or weakened assertions. Check exact/adjacent score gaps, ID collisions/duplicates, ordinary decimal weights and extreme-value rejection. A separate review must report its actual SHA and findings; no response is not an approval.

After merge, verify fresh push CI on the actual main commit. Tag/release publication is separate and must resolve to the accepted commit; do not reuse the 0.2.1 distribution evidence record or claim that an older CI run covered this version.

## Unchanged limitations

BUY_NEW and BUY_USED stay method-blocked. No market catalog, research service, public-agent CLI, completed ten-case pilot or multi-provider conformance is introduced. PC-01 remains explicitly unresolved. D2 preserves reconstruction fingerprints while retiring reconstructed XLSX distribution. Private RC1 source packages remain outside the public boundary.

Ordinary owner attribution and inspected non-sensitive historical comparison context are accepted under `PRIVACY_SCOPE_2026-09-07.md`. Sensitive records remain excluded; no history rewrite or blanket privacy clearance is implied.

See `REPAIR_CHANGELOG_0.2.2.md` for the chronological repair ledger and `PRODUCTION_READINESS.md` for activation gates.
