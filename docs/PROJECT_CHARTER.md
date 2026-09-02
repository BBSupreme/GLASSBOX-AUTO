# Project Charter

## Mission

Build an open, auditable and reproducible decision-support system for private car acquisition in Denmark, spanning private leasing, new-car purchase and used-car purchase.

The system should help a user answer not only **“which car is best?”**, but:

- Which acquisition mode is economically rational under my assumptions?
- Which vehicles satisfy my must-haves?
- Which candidates are close calls rather than false precision?
- Which conclusions are supported by strong evidence, and which depend on missing or estimated data?
- What would have to change for the recommendation to change?

## Design goal

The system must be:

- **Simple enough to inspect**
- **Scalable enough to cover a broad market**
- **Configurable enough for individual household priorities**
- **Efficient enough to update as offers and evidence change**
- **Explicit enough to survive adversarial review**

## Non-goals

GLASSBOX-AUTO is not intended to:

- hide subjective preferences behind an unexplained score;
- promote manufacturer claims as verified facts;
- pretend that missing data is certainty;
- collapse financing cash flow and economic cost into one number;
- provide regulated financial, legal, tax, insurance or safety advice.

## Decision object model

The project separates:

### Vehicle
The underlying make/model/variant/configuration and its relatively stable technical attributes.

### Acquisition_Offer
A market offer attached to a vehicle: leasing, new purchase, or used purchase, with price, term, mileage, financing and commercial conditions.

### Decision_Candidate
The normalized comparison object consumed by the decision engine.

This separation is intended to prevent a transient commercial offer from contaminating the underlying vehicle record, and to allow one vehicle to appear under multiple acquisition modes.

## User model

The system is individualized by editable preferences, weights and gates. A default profile may exist, but it must not become hidden hard-coded truth.

A **Must-have** requirement is both:

1. weighted as Very High; and
2. enforced as a decision-critical gate.

## Evidence model

Evidence should distinguish at least:

- VERIFIED
- ESTIMATED
- UNKNOWN / MISSING

A modeled real-world range estimate remains ESTIMATED. VERIFIED requires matched measurement evidence rather than a model-generated value.

## Decision integrity

The system should expose:

- active/inert/excluded weights;
- total evidence coverage;
- decision-critical unknowns;
- close-call state;
- source dates;
- assumptions and scenario inputs;
- tie-breaking behavior;
- break-even conditions where relevant.

## Open-source principle

The project is public so that assumptions, methods and mistakes can be inspected. Contributions should improve evidence quality, coverage, reproducibility or decision logic rather than simply add more opaque scoring.