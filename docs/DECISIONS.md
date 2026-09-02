# Canonical Decision Log

This file records decisions that should be treated as binding unless explicitly superseded by a later documented decision.

## Leasingmatrix 2026 v3 — Revision A

Revision A dated 2026-08-29 is binding over the earlier v3 handover where they conflict.

### D-V3.21 — Must-have semantics
A Must-have criterion creates a decision-critical gate and also receives Very High weighting.

### D-V3.22 — Default label multipliers
Default preference multipliers:

- Low = 0.5
- Medium = 1.0
- High = 1.5
- Very High = 2.0
- Must-have = 2.0 + gate

Weights are normalized to 100% over active/scorable criteria.

### D-V3.23 — Missing-data treatment
Missing data is not silently converted to a zero score. Normalized weighting excludes missing values from the scored denominator, while evidence coverage and readiness expose the resulting uncertainty.

### D-V3.24 — Close-call threshold
Use a close-call threshold of:

- 0.20 when evidence-weight coverage is below 95%;
- 0.15 when evidence-weight coverage is at or above 95%.

A close call should be surfaced as such rather than hidden behind rank order.

### D-V3.25 — Safety placement
Safety is a gate plus capped child-protection evidence within the Family dimension. It does not receive a separate standalone weight that can double-count the same concern.

### D-V3.26 — Readiness
Readiness depends on decision-critical unknowns and close-call state, not on arbitrary completeness targets alone.

### D-V3.27 — Gates require operational definitions
Every gate must specify how it is evaluated, what data is required, and what happens when the required evidence is missing.

### D-V3.28 — Diminishing utility
Diminishing utility uses fixed piecewise-linear Floor / Need / Stretch anchors rather than opaque nonlinear scoring.

### D-V3.29 — QA scope
QA must include, at minimum:

- field/mapping tests;
- utility-curve tests;
- deterministic tie behavior;
- frontend hard-code scan;
- Excel compatibility;
- LibreOffice compatibility.

### D-V3.30 — Evidence semantics and profile transparency
Modeled real-world range is ESTIMATED. VERIFIED requires matched measurement evidence.

Evidence collection is prioritized for shortlist candidates, gates and promotion triggers.

The minimum profile view must expose inert/excluded weights and total evidence coverage.

## Additional method decisions already established in v3 work

- Dead weights should be removed rather than preserved as decorative settings.
- Baggage utility was split into an 8 + 2 treatment in the v3 refinement.
- A liquidity guard is part of the economics treatment.
- Mileage fit must account for the cost of unused contracted kilometres, not only overage risk.
- Family subweights are editable.
- Ranking must be deterministic.

## Acquisition & Purchase Layer — preserved architectural decisions

The following Draft A decisions survived adversarial review and should be preserved:

1. Separate `Vehicle`, `Acquisition_Offer`, and `Decision_Candidate`.
2. Loan principal is not economic cost.
3. Residual value must be scenario-based rather than represented as a single unjustified point estimate.
4. Break-even residual value is mandatory in lease-vs-buy comparison.

The acquisition/purchase layer is **not yet implementation-approved as a complete method**. See `ACQUISITION_PURCHASE_LAYER.md`.