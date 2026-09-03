# Canonical Decision Log

This file records decisions that should be treated as binding unless explicitly superseded by a later documented decision.

## Leasingmatrix 2026 v3 — Revision A

Revision A dated 2026-08-29 is binding over the earlier v3 handover where they conflict. The numbering and wording below are corrected from the recovered exact `HANDOVER_ADDENDUM_v3_RevA.md`.

### D-V3.21 — Must-have semantics
Must-have in Priorities spawns a decision-critical gate on the underlying attribute and is weighted as Very High. Must-have does not create a separate weight level beyond the 2.0 multiplier + gate translation.

### D-V3.22 — Default label multipliers
Default translation:

- Low = 0.5
- Medium = 1.0
- High = 1.5
- Very High = 2.0
- Must-have = 2.0 + gate

Base dimension weights for the default v3 profile are:

- Economics = 35
- Practical/Family = 25
- Comfort & Driving = 15
- EV Usability = 15
- Equipment & UX = 10

Effective weights are base × multiplier and normalized to 100%. Numeric weights remain available in Advanced mode.

### D-V3.23 — Close-call threshold
Use a coverage-dependent close-call threshold:

- 0.20 when weight coverage is below 95%;
- 0.15 when weight coverage is at or above 95%.

The recovered v3/v3.2 workbook currently uses a four-item critical-evidence coverage measure for this switch, which conflicts with the exact Revision A wording (`weight coverage`). Keep that implementation/spec conflict explicit until the later v3.2.1 fixture is recovered.

### D-V3.24 — Safety placement
Safety is:

1. a gate based on Euro NCAP stars plus protocol-year/generation match; and
2. capped Euro NCAP child-protection evidence inside Practical/Family.

There is no standalone Safety weight in v3.

The recovered implemented profile uses Family subweights of 30% baggage, 25% by-fit, 30% child-seat/stroller and 15% child protection, with UNKNOWN child protection excluded and the Family denominator renormalized.

### D-V3.25 — Readiness
Readiness is a function of decision-critical unknowns and close-call state only. Non-critical gaps affect Confidence rather than Readiness.

Recovered implementation semantics clarify the gate/ranking boundary:

- gate `FAIL` → INELIGIBLE;
- gate `UNKNOWN` may remain ranked but prevents READY where decision-critical.

### D-V3.26 — Gates require operational definitions
Every gate must specify the underlying fields, evaluation rule, required evidence and missing-data behavior. An undefined gate is not created.

The recovered Revision A explicitly operationalizes acceptable lease terms through fields such as binding period, known minimum price in binding, and known termination/return terms.

### D-V3.27 — Diminishing utility
Diminishing utility is piecewise linear with fixed Floor / Need / Stretch anchors:

- Floor → 0 points
- Need → 8 points
- Stretch → 10 points

Therefore canonical v3 Need utility is 0.8 on a normalized 0–1 scale.

Recovered default anchors:

- Real range: F=200 / N=350 / S=500 km
- Baggage: F=300 / N=profile requirement (default 500) / S=600 L
- DC 10–80: F=45 / N=28 / S=18 min, lower is better

The recovered implemented v3 also uses child protection 70%→0 and 95%→10 within Family.

### D-V3.28 — Real-range evidence
Modeled real-world range is ESTIMATED. VERIFIED requires a generation/variant-matched measurement from an independent instrumented test or own logging.

### D-V3.29 — Evidence scope
Evidence collection is scoped to shortlist candidates, gate attributes for all candidates, and datapoints that can trigger WATCH→SHORTLIST promotion. Full-catalog attribute evidence is explicitly out of scope.

### D-V3.30 — Profile transparency
The minimum-profile surface must show whether each dimension is active, inert/no-variation, or excluded due to missing data, plus total coverage. A user must not be led to believe a weight is working when it is mathematically inactive.

## Earlier/interim v2.1 refinements — historical, not automatically v3 dimensions

The recovered v2.1 workbook confirms the following interim behavior before the full v3 five-dimension rebuild:

- dead weights were excluded from the active score denominator;
- baggage used an interim 8+2 treatment;
- liquidity was a **score**, not a gate, using preferred limits of 30,000 DKK first payment and 85,000 DKK first-12-month cash burden plus a 50% blend with relative-to-cheapest;
- km-fit included a penalty for unused contracted kilometres;
- Family subweights were editable;
- ranking was deterministic.

The full recovered v3 architecture no longer exposes standalone Liquidity or Km-fit dimensions. These interim refinements must therefore not be treated as binding v3 gates/dimensions unless the missing v3.2.1 artifact explicitly reintroduces them.

## Acquisition & Purchase Layer — preserved architectural decisions

The following Draft A decisions survived the later adversarial review summary and should be preserved structurally:

1. Separate `Vehicle`, `Acquisition_Offer`, and `Decision_Candidate`.
2. Loan principal is not economic cost.
3. Residual value must be scenario-based rather than represented as a single unjustified point estimate.
4. Break-even residual value is mandatory in lease-vs-buy comparison.

The acquisition/purchase layer is **not implementation-approved as a complete method**. Exact Draft A source, P1–P3 wording/findings and purchase Economics Floor/Need/Stretch anchors remain to be recovered.