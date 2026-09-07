# Readiness integrity repair ledger — planned 0.2.2

Date: 2026-09-07. Status: UNRELEASED / independent review required.
Base: `55e82c378f94e0ea1b6481b405c6cb7053f6b9f8` (Engine 0.2.1).

This is a narrow source repair, not a released 0.2.2 package. Package/runtime
version remains 0.2.1 while under review; exact commit identifies the candidate.
Do not distribute the candidate under that version. Before merge/release, bump
metadata/runtime/smoke tests to 0.2.2, align README/production/release notes and
CHANGELOG.md, then rerun all gates on that new head. No main change is implied.

## Change record

| Finding | Correction | Preserved test / acceptance |
|---|---|---|
| #11 / AR-B-01 | Inclusive gap comparison permits only absolute round-off tolerance 1e-12 score points, with zero relative tolerance. | 0.15/0.20 exact and +/-1e-8 boundary cases at five score levels; +1e-10 remains outside. |
| #12 / AR-B-02 | Percent-encode each ID component, then join with colon; reject duplicates of serialized IDs AND original pairs before ranking. | Colon/percent/space/Unicode corpus, invalid IDs, pair duplicates, order permutations and exact ties. |
| #13 / AR-B-03 | Reject non-finite effective weights (before caps), totals, utilities, spans, economics and result leaves; validate score/coverage bounds before ranking. | Sum/product/cap overflow; safe ratio-before-scale, mileage overflow incl inf-inf, nested NaN, valid large weights and ordinary economics. |
| AR-A-01/02 | Owner accepts the inspected ordinary footprint; sensitive data remains protected. | Separate dated privacy-scope decision; no history rewrite or anonymity claim. |

## Numerical policy v1

The score is on a 0–10 scale. `gap <= threshold` remains the first comparison;
`math.isclose(gap, threshold, rel_tol=0, abs_tol=1e-12)` handles equality obscured
by binary round-off. This is a documented tiny boundary allowance, not proof of
exact real-number arithmetic. It may classify gaps within 1e-12 above the band
as close; wider gaps must not be absorbed. Scores are not rounded for ranking.
The 0.95 coverage switch and PC-01 source-track distinction are unchanged.

Non-finite arithmetic raises NumericalIntegrityError (a ValueError subtype).
Missing evidence remains missing; it is not used to disguise numeric failure.
Finite but unrepresentable intermediate magnitudes can be rejected, even when
an algebraically rearranged calculation could be finite. No arbitrary clamping
or zero substitution. This patch is not a general arbitrary-precision engine.

## Self-review correction before independent review

The first 101-test patch passed repository CI (190 tests on the Python 3.11 leg;
all four runtime legs green), but a deterministic normal-weight stress probe
then exposed a new guard rejection. Python 3.13's compensated built-in sum for
the denominator could disagree with sequential += coverage numerators by one
round-off step. The guard correctly refused coverage above one, but these were
valid ordinary weights and should not be rejected.

All scoring aggregates now use the same math.fsum algorithm, with explicit
finite-sum overflow errors. Divide weighted utility by its denominator before
multiplying by ten, avoiding unnecessary overflow on a representable mean.
Retain the exact reproducer and 60 seeded anchor controls. No display rounding,
clamping, weakened coverage bound or removed original review assertion.
New code requires new exact-head CI; do not reuse the first patch's results.

## Identity migration

Ordinary unreserved IDs such as `car-1:offer_2` are unchanged. `a:b` / `c`
becomes `a%3Ab:c`; `a` / `b:c` becomes `a:b%3Ac`; percent signs are themselves
escaped. Raw vehicle_id and offer_id remain authoritative components. Consumers
must not reconstruct identities by unescaped concatenation. Empty/control or
invalid UTF-8 identifiers fail explicitly. Previously persisted IDs containing
reserved characters must be rebuilt from the two raw component fields.

## Execution evidence at preparation

- Five baseline core modules matched their recorded Git blob SHAs before tests.
- The unchanged 27-test review suite reproduced 6 failures / 21 passes.
- After correction the same 27 assertions pass, with no xfail or skipped test.
- 135 additional parameterized boundary/integrity controls pass: 162 total local
  tests, Python 3.13.5 / pytest 9.0.2. Source compilation passes.
- Local runtime is a byte-verified core snapshot, not a complete clone. Original
  full suite, compatibility and wheel packaging are delegated to exact-head CI.
- CI retains the four categories and runs the complete suite on Python
  3.11/3.12/3.13/3.14. Record actual completed results on the PR; configuration
  alone is not execution evidence. All four matrix legs are required.

## Review and scope

Builder self-review is not independent approval. A separate reviewer must attack
numeric tolerance breadth, reserved-ID migration, duplicate handling, overflow
failure behavior and the unchanged default/strict UNKNOWN semantics. Block merge
on a material defect or absent evidence. Do not infer supported AI providers or
current-market validity from passing engine tests.

Purchase methods, live-market policy, PC-01 authority, RC1 workbook rebuilding,
public schemas/CLI, and ten-case pilot remain separate. Continue with the reduced
request/result interface only after its amendment is accepted.

Research references:
- https://docs.python.org/3/library/math.html#math.isclose
- https://docs.python.org/3/library/math.html#math.isfinite
- https://docs.python.org/3/library/urllib.parse.html#urllib.parse.quote
