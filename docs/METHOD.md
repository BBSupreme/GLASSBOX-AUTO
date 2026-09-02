# Decision Method

## 1. Overview

GLASSBOX-AUTO compares cars and acquisition offers through an explicit pipeline:

```text
source evidence
    ↓
normalized vehicle + offer data
    ↓
operational gates
    ↓
criterion utility
    ↓
weighted score + evidence coverage
    ↓
close-call/readiness logic
    ↓
economic scenarios
    ↓
recommendation + falsifiers
```

A ranking is not considered decision-ready merely because a numeric score exists.

## 2. Criteria, weights and gates

Each relevant user criterion has:

- a preference label;
- a numeric multiplier;
- an operational definition;
- source/evidence requirements;
- a utility function;
- optional gate behavior.

Default multipliers are:

| Label | Multiplier | Gate |
|---|---:|---|
| Low | 0.5 | No |
| Medium | 1.0 | No |
| High | 1.5 | No |
| Very High | 2.0 | No |
| Must-have | 2.0 | Yes |

Weights are normalized across active, scorable criteria. Missing data is excluded from the scoring denominator; it must still reduce evidence coverage and can block readiness.

## 3. Utility curves

Where more is not linearly better forever, the method uses fixed piecewise-linear anchors:

- **Floor** — below this point utility is inadequate or very low;
- **Need** — the point where the practical requirement is satisfied;
- **Stretch** — additional benefit above Need, with diminishing decision value.

This structure should be inspectable from inputs alone and testable with boundary cases.

## 4. Gates

A gate must specify:

- required field(s);
- threshold or boolean condition;
- evidence grade required;
- result if data is missing;
- result if the condition fails.

`UNKNOWN` is not automatically equal to `FAIL`. For decision-critical gates, missing evidence should normally make the candidate not-ready pending verification.

## 5. Evidence and coverage

Evidence is not just a citation field; it affects decision confidence.

At minimum, distinguish:

- `VERIFIED`
- `ESTIMATED`
- `UNKNOWN`

A model-derived value cannot promote itself to VERIFIED.

Evidence collection should be prioritized where it can change the decision:

1. must-have gates;
2. shortlist candidates;
3. promotion/demotion triggers;
4. close-call differentiators.

## 6. Close calls

Rank order is not enough. If the score difference between leading candidates is within the configured falsification band, the decision is surfaced as a close call.

Canonical thresholds:

- gap ≤ 0.20 when evidence-weight coverage < 95%;
- gap ≤ 0.15 when evidence-weight coverage ≥ 95%.

The purpose is to avoid false precision and direct research toward evidence likely to resolve the decision.

## 7. Readiness

Readiness is driven by:

- unresolved decision-critical unknowns;
- failed or unresolved gates;
- close-call state;
- sufficient evidence for decision-critical distinctions.

Completeness for its own sake is not the objective.

## 8. Mileage fit

Leasing comparisons must account for both:

- overage exposure when expected mileage exceeds the contract allowance; and
- value lost when a household pays for materially more kilometres than it expects to use.

The canonical project profile historically used 15,000 km/year as the normal comparison and 20,000 km/year as a stress case. These are profile/scenario inputs, not universal constants.

## 9. Economics

Economic comparison must keep separate:

- cash paid;
- financing cash flow;
- interest/fees;
- depreciation/equity change;
- residual value;
- economic cost.

For purchase candidates, principal repayment builds equity and therefore must not be counted as economic consumption in the same way as interest or depreciation.

Lease-vs-buy analysis requires scenario-based residual values and a break-even residual.

## 10. Candidate promotion

A candidate should not be promoted solely because it has the highest score. Promotion should consider:

- gates passed;
- score;
- evidence coverage;
- readiness;
- close-call status;
- economics;
- sensitivity to key assumptions.

## 11. Output contract

A decision-facing output should make it possible to answer:

- Why is this candidate ranked here?
- Which inputs drove the result?
- What evidence is weak or missing?
- Which gate matters?
- What assumption would flip the recommendation?
- Is the difference material or merely numerical?
