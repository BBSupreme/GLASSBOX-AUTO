# Readiness integrity repair ledger — 0.2.2 candidate

Date: 2026-09-07. Status: UNRELEASED / separate review and activation gates required.
Base: `55e82c378f94e0ea1b6481b405c6cb7053f6b9f8` (Engine 0.2.1).

This is a narrow repair, not the public-agent interface. The initial source-only
review commits kept 0.2.1 metadata; the release-preparation step below aligns the
candidate package/runtime/smoke expectations on 0.2.2. Neither identity nor an
older green run permits distribution before the current review and CI gates.

## Change record

| Finding | Correction | Preserved test / acceptance |
|---|---|---|
| #11 / AR-B-01 | Inclusive gap comparison permits only absolute round-off tolerance 1e-12 score points, with zero relative tolerance. | 0.15/0.20 exact and +/-1e-8 boundary cases at five score levels; +1e-10 remains outside. |
| #12 / AR-B-02 | Percent-encode each ID component, then join with colon; reject duplicates of serialized IDs AND original pairs before ranking. | Colon/percent/space/Unicode corpus, invalid IDs, pair duplicates, order permutations and exact ties. |
| #13 / AR-B-03 | Reject non-finite effective weights (before caps), totals, utilities, spans, economics and result leaves; validate score/coverage bounds before ranking. | Sum/product/cap overflow; safe ratio-before-scale, mileage overflow incl inf-inf, nested NaN, valid large weights and ordinary economics. |
| AR-A-01/02 | Owner accepts the inspected ordinary footprint; sensitive data remains protected. | Separate dated privacy-scope decision; no history rewrite or anonymity claim. |
| Codex P2 / 3952286063 | Validate canonical serialized candidate ID against raw vehicle/offer fields during evaluation and reranking. | Reject legacy/inconsistent IDs instead of silently returning or migrating ambiguous cached identity. |
| Codex P2 / 3952286068 | Reject Unicode Cc controls, Cf format controls and Zl/Zp line/paragraph separators in raw IDs. | C1/newline/bidi/format corpus rejected; ordinary accented/CJK and correctly encoded reserved IDs retained. |

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

Following the separate review, reranking rejects any candidate_id inconsistent
with the canonical encoding of those raw fields, including legacy IDs and
caller-supplied custom identities. There is no silent cache migration. Duplicate
diagnostics are retained before canonical-mismatch diagnostics for repeated IDs
or pairs. Raw IDs reject Unicode general categories Cc/Cf/Zl/Zp; ordinary Unicode
letters and permitted spaces/reserved characters retain their explicit encoding.
This is not a general Unicode-confusable or display-name sanitizer.

## Initial source execution evidence

- Five baseline core modules matched their recorded Git blob SHAs before tests.
- The unchanged 27-test review suite reproduced 6 failures / 21 passes.
- After correction the same 27 assertions passed, with no xfail or skipped test.
- 135 additional parameterized boundary/integrity controls passed: 162 total local
  tests, Python 3.13.5 / pytest 9.0.2. Source compilation passed.
- Local runtime was a byte-verified core snapshot, not a complete clone. Original
  full suite, compatibility and wheel packaging were verified separately by CI.
- CI `34154202209` completed successfully for repair head `f5af174` across core,
  historical compatibility, release/wheel and all four regression runtimes.
  PR synthetic merge `86e8d8d5f2497e0c00df0711b44c3d33453689c8` had the same tree
  `87ff9f6864679dab5467b6290f778a69bb64f197`; it was not a main release.

## Review execution and release-identity preparation

A separate Codex code-review request was posted on PR #14 as comment
`5574922480`, targeting `f5af174`. The bot acknowledged RUNNING in comment
`5574925082`. Final release-prepared head `44448eab1afac195706fb3371abcd9fbb1b5afbf`
was submitted in comment `5574981730`; its fresh CI `34156417968` passed all
seven jobs, including four regression runtimes.

The coordinating assistant also recovered six core modules, verified their Git
blob identities against `f5af174`, and reran the original 27 falsifiers: 27 PASS
on Python 3.13.5. This is additional builder execution, not independent approval
and not a local run of the full repository suite.

Release preparation aligned pyproject, runtime version, release-integrity tests,
wheel smoke, README, production notes and global CHANGELOG on 0.2.2, and added
`RELEASE_0.2.2.md`. It did not change decision-math modules.

## Separate reviewer findings and correction

At 2026-09-07T19:46:12Z the actual Codex reviewer submitted a review for
`44448eab1a` with two P2 findings: canonical identity not enforced on reranking
(comment 3952286063), and Unicode C1 control characters accepted by ASCII-only
validation (3952286068). This is a completed review with findings, NOT approval.
The bot did not report a test-run total; none is attributed to it here.

Both reports were accepted and independently reproduced by the coordinating
assistant on the source snapshot. Nineteen new parameterized controls include
four noncanonical-ID cases, eight control/format/line-separator cases, six valid
roundtrip controls and duplicate-diagnostic preservation. Before correction:
12 FAIL / 7 PASS. After correction: all 19 PASS plus the original 27 unchanged,
46 PASS total locally on Python 3.13.5. Source compilation passed. No original
assertion was softened; full repository/runtime checks are delegated to new CI.

The new source requires fresh CI and re-review. Preserve the findings and their
resolution replies; do not infer approval from obsolete threads or prior green
runs. Publication remains governed by `PRODUCTION_READINESS.md`.

## Review and scope

Builder self-review is not independent approval. A separate reviewer must attack
numeric tolerance breadth, reserved-ID migration, duplicate handling, overflow
failure behavior and unchanged default/strict UNKNOWN semantics. Block merge
on a material defect or absent evidence. Do not infer supported AI providers or
current-market validity from passing engine tests.

Purchase methods, live-market policy, PC-01 authority, RC1 workbook rebuilding,
public schemas/CLI, and ten-case pilot remain separate. Continue with the reduced
request/result interface only after its amendment is accepted.

Research references:
- https://docs.python.org/3/library/math.html#math.isclose
- https://docs.python.org/3/library/math.html#math.isfinite
- https://docs.python.org/3/library/urllib.parse.html#urllib.parse.quote
- https://docs.python.org/3/library/unicodedata.html#unicodedata.category
- https://openai.com/index/introducing-upgrades-to-codex/
