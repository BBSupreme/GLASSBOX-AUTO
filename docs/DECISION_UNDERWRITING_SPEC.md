# Decision Underwriting — Product & Method Specification

## Status

**Branch:** `product/decision-underwriting`  
**Status:** SPEC / exploratory; not approved for production  
**Reference use case:** real-world car questions such as a first-time buyer asking whether a specific used car at a specific price is a sensible purchase.

This specification extends the existing GLASSBOX-AUTO decision method without changing the canonical method on `main`. It deliberately treats Reddit as a reference interaction pattern and source of acceptance cases, not as a platform dependency.

---

## 1. Product thesis

GLASSBOX-AUTO should accept the car decision a user is already trying to make and determine which analysis path is required.

The primary interaction should be closer to:

> “Here is the car / offer / shortlist / situation I am considering. What should I do?”

than:

> “Configure a scoring matrix before the system can help me.”

The engine remains a glass box: every conclusion must be traceable to source evidence, normalization, assumptions, decision logic, uncertainty and falsifiers.

### Core capability

**Decision Underwriting** converts a natural-language car decision into an inspectable decision case, researches only the evidence capable of changing that decision, and returns a recommendation whose assumptions and failure conditions are explicit.

---

## 2. User jobs

The front end should classify the decision into one or more user jobs rather than require the user to choose an internal acquisition mode.

### DISCOVER

“I need a car; what should I look at?”

Output focus:
- requirement extraction;
- must-have gates;
- candidate generation;
- shortlist;
- unresolved profile questions that are decision-critical.

### COMPARE

“Enyaq or IONIQ 5?”

Output focus:
- normalized candidates;
- meaningful differentiators;
- close-call logic;
- sensitivity to preferences and evidence gaps.

### UNDERWRITE

“Is this specific Fiesta at DKK 28,000 a sensible buy?”

Output focus:
- the concrete vehicle instance;
- price/deal quality;
- condition/history risks;
- expected near-term costs;
- model-specific failure modes;
- inspection checklist;
- walk-away conditions.

### CHOOSE_ACQUISITION

“Should I lease, buy new or buy used?”

Output focus:
- acquisition economics;
- cash flow versus economic cost;
- residual scenarios;
- break-even residual;
- downside and flexibility.

### VERIFY

“Is this advertised offer actually as good as it looks?”

Output focus:
- source validation;
- omitted fees/conditions;
- comparable market offers;
- stale or misleading claims;
- promotion/demotion triggers.

A case may contain multiple jobs. Classification is routing, not a scoring factor.

---

## 3. Reference interaction

Minimum acceptable user input is unstructured text, a market/listing URL, or both.

Example:

> First-time buyer, student. Ford Fiesta 1.25 60 Trend, 2011, 111,000 km. Seller says timing belt was changed in 2019 at 82,000 km. Price negotiated to DKK 28,000. Is it sensible and what should I inspect?

The system should infer that this is primarily `UNDERWRITE`, acquisition mode `BUY_USED`, while preserving uncertainty around any field not directly supported by evidence.

The system must not require the user to know internal terms such as `BUY_USED`, utility curves or evidence grades.

---

## 4. Decision case object

Introduce a case-level object above the existing comparison objects.

```text
Decision_Case
├── user_job[]
├── user_context
├── stated_requirements
├── inferred_requirements
├── assumptions
├── candidate_refs[]
├── evidence_refs[]
├── critical_unknowns[]
├── research_tasks[]
├── readiness
└── recommendation
```

### Requirement provenance

Every requirement must be labelled as one of:

- `STATED` — directly supplied by the user;
- `INFERRED` — derived from context and exposed for correction;
- `DEFAULT` — system default, explicitly visible;
- `UNKNOWN` — relevant but not established.

An inferred preference may guide research priority, but must not silently become a hard gate.

---

## 5. Vehicle instance layer

The current architecture separates:

```text
Vehicle
Acquisition_Offer
Decision_Candidate
```

Concrete used-car underwriting requires an additional object:

```text
Vehicle
   ↓
Vehicle_Instance
   ↓
Acquisition_Offer
   ↓
Decision_Candidate
```

### Vehicle

Stable make/model/variant/configuration data.

Examples:
- make;
- model;
- generation;
- engine/battery variant;
- equipment grade;
- technical specifications;
- known model/generation characteristics.

### Vehicle_Instance

The specific physical car being considered.

Candidate fields include:
- registration/VIN where lawfully and intentionally supplied;
- first registration / model year;
- odometer;
- owner count where available;
- service history;
- maintenance records;
- timing-belt/chain evidence;
- battery state of health for EVs where available;
- inspection/syn history;
- accident/repair history;
- corrosion/rust evidence;
- tyres;
- brakes;
- warning lights/fault codes;
- cosmetic condition;
- modifications;
- known immediate maintenance needs;
- seller assertions;
- independent inspection findings.

### Why the layer is required

Two cars with identical model specifications and odometer readings can have materially different economic risk because their maintenance, condition and provenance differ. These differences belong to the physical vehicle instance, not the stable `Vehicle` record and not solely to the commercial offer.

`Vehicle_Instance` is proposed by this branch and is **not canonical until method review approves it**.

---

## 6. Acquisition offer

For used-car underwriting, `Acquisition_Offer` should include at minimum:

- asking price;
- negotiated price;
- private/dealer sale;
- warranty / reklamationsret context where applicable;
- trade-in;
- financing terms if relevant;
- fees;
- included accessories/tyres;
- location;
- listing timestamp;
- seller claims;
- expiry/availability state.

The system must distinguish the quality of the vehicle from the quality of the deal.

A good vehicle can be a bad deal. A low price can still be a bad purchase.

---

## 7. Evidence model extension

Keep the canonical certainty states:

- `VERIFIED`
- `ESTIMATED`
- `UNKNOWN`

Add evidence-source class independently from certainty.

Proposed source classes:

- `PRIMARY_OFFICIAL` — manufacturer documentation, authority/registry data, official service documentation;
- `INDEPENDENT_TEST` — reputable independent automotive testing or inspection;
- `MARKET_LISTING` — live or archived marketplace/dealer listing;
- `SELLER_CLAIM` — unverified statement by seller;
- `OWNER_REPORT` — individual owner experience;
- `COMMUNITY_PATTERN` — repeated user reports with documented provenance;
- `MODEL_DERIVED` — calculated or inferred by GLASSBOX;
- `USER_SUPPLIED` — document/photo/fact supplied by the user without independent verification.

### Rule

Source class and certainty must never be collapsed into one field.

Examples:

```text
Timing belt changed in 2019
source_class = SELLER_CLAIM
certainty = UNKNOWN or unverified
```

```text
Invoice from workshop shows belt replacement
source_class = USER_SUPPLIED / PRIMARY_OFFICIAL depending on verification path
certainty = VERIFIED
```

Multiple owner reports may justify research priority but must not automatically promote a claim to `VERIFIED`.

---

## 8. Intake pipeline

```text
raw user input / URL
        ↓
intent + user-job classification
        ↓
entity extraction
        ↓
requirement extraction
        ↓
Decision_Case draft
        ↓
critical-unknown detection
        ↓
research plan
        ↓
evidence acquisition
        ↓
Vehicle / Vehicle_Instance / Acquisition_Offer normalization
        ↓
gates + economics + utility where relevant
        ↓
readiness
        ↓
recommendation + falsifiers + action checklist
```

### Entity extraction must preserve uncertainty

The parser must not invent missing trim, engine, model year, price, mileage, ownership or service data.

Conflicting values must survive as conflict state until resolved.

---

## 9. Research policy

Research is decision-directed rather than completeness-directed.

Priority order:

1. facts required for must-have gates;
2. facts capable of making the candidate unsafe or economically irrational;
3. evidence capable of materially changing the recommendation;
4. market comparables needed to evaluate deal quality;
5. close-call differentiators;
6. lower-value enrichment.

### Used-car underwriting research domains

Depending on the case:
- model/generation reliability patterns;
- maintenance schedule;
- timing-belt/chain requirements;
- recalls/service campaigns;
- inspection history;
- market-price comparables;
- insurance/tax/energy inputs where economically material;
- expected near-term consumables and maintenance;
- EV battery warranty and battery-health evidence;
- independent road tests relevant to the user’s stated needs.

Research must expose source dates because market price and offer data age quickly.

---

## 10. Underwriting gates

A used-car decision may include gates such as:

### Identity gate

Do the listing, registration and physical car describe the same vehicle/variant?

### History gate

Are decision-critical maintenance claims documented to the evidence level required for the decision?

### Condition gate

Are there unresolved defects with plausible cost or safety impact large enough to dominate the purchase economics?

### Legality/inspection gate

Are required inspection/registration conditions acceptable and understood?

### Budget resilience gate

Can the user absorb plausible near-term repair/maintenance exposure without violating a stated budget constraint?

### Fit gates

Any user-specific must-have requirements such as seats, child-seat fit, towing, range, access, dimensions or other operational requirements.

Exact gate definitions and thresholds require separate method approval. `UNKNOWN` must remain distinct from `FAIL`.

---

## 11. Economics for a concrete used car

The engine should show separate views for:

- purchase cash required;
- financing cash flow if applicable;
- expected running costs;
- expected scheduled maintenance;
- immediate known maintenance;
- risk reserve / scenario repair exposure;
- expected residual-value scenarios;
- economic cost over the intended holding period.

A low purchase price must not dominate the decision if plausible immediate repairs materially alter total cost.

Where uncertainty is high, present scenarios rather than unsupported point estimates.

Purchase principal remains separate from economic consumption, consistent with the canonical acquisition-layer rule.

---

## 12. Recommendation states

Avoid false precision from a single score.

Proposed user-facing states:

### GREEN — Decision-ready / attractive

Evidence is sufficient for the material claims, no critical gate is unresolved, and economics/fit support the decision.

### YELLOW — Potentially attractive / verify first

Candidate may be sensible, but one or more decision-critical unknowns remain. Provide the exact verification actions required.

### RED — Do not proceed under current facts

A failed gate, adverse economics, material condition risk or incompatible requirement dominates the decision.

### INSUFFICIENT_DATA

The system cannot responsibly distinguish the decision because required evidence is absent.

These labels are presentation states; internal readiness must remain inspectable.

---

## 13. Output contract

Every underwriting output must answer, in plain language:

1. **What is the decision?**
2. **What do we know?**
3. **What is inferred?**
4. **What is critically unknown?**
5. **What argues for the candidate?**
6. **What argues against it?**
7. **Is the price/deal attractive relative to the relevant market?**
8. **What should the user inspect or verify before acting?**
9. **What would make us walk away?**
10. **What fact would flip the recommendation?**
11. **How confident/readiness-qualified is the conclusion?**
12. **Which sources support the material claims?**

### Compact channel output

The engine should be able to render a 200–400 word answer suitable for a forum, chat or comment while linking to or preserving the full evidence trace separately.

The compact answer must never imply more certainty than the full case state.

---

## 14. Reddit as reference UX, not dependency

Reddit is useful because typical posts contain natural user context, imperfect information and genuine decision pressure.

The product must not depend on:
- Reddit authentication;
- automated posting;
- subreddit-specific APIs;
- scraping private/user-sensitive data;
- Reddit-specific scoring logic.

Instead, public questions can become test fixtures where legally and ethically appropriate.

Desired loop:

```text
real-world question
    ↓
GLASSBOX Decision Case
    ↓
inspectable analysis
    ↓
compact useful answer
    ↓
community correction / new evidence
    ↓
evidence review
    ↓
improved case or reusable knowledge
```

Community claims remain evidence, not truth.

---

## 15. Acceptance corpus

Create a versioned corpus of de-identified or public-link decision cases spanning at least:

- first used car under DKK 50k;
- high-mileage commuter;
- family car with child-seat/space constraints;
- used EV with battery/range concerns;
- “good price from a friend” private-sale case;
- new vs used EV;
- lease vs buy;
- second car with very low annual mileage;
- two-car comparison;
- concrete lease-offer verification;
- model with known maintenance controversy;
- incomplete listing / conflicting seller claims.

### Minimum corpus size for first evaluation

**50 cases.**

Each fixture should contain:

```text
case_id
source/reference
raw_question
expected_user_job
known_facts
expected_unknowns
candidate_entities
required_research_domains
minimum_safe_output
prohibited_overclaims
```

The corpus tests reasoning and evidence discipline, not agreement with Reddit comments.

---

## 16. Acceptance criteria

The Decision Underwriting capability is not ready for public promotion until it can demonstrate all of the following on the acceptance corpus:

### Intake
- ≥95% correct acquisition-mode extraction where explicitly stated or unambiguous;
- no fabricated decision-critical vehicle/offer facts;
- stated and inferred requirements remain distinguishable.

### Evidence
- all material claims trace to source evidence or are labelled inference/estimate;
- seller/community claims cannot silently become `VERIFIED`;
- stale offer/market evidence is exposed.

### Decision integrity
- critical unknowns block readiness when appropriate;
- `UNKNOWN` is not collapsed into `FAIL`;
- recommendation includes explicit falsifier/walk-away condition;
- close calls are surfaced rather than forced into false rank precision.

### Used-car layer
- Vehicle and Vehicle_Instance facts remain separated;
- condition/history can alter recommendation independently of model score;
- deal quality is evaluated separately from vehicle quality.

### Output
- full audit trace exists;
- compact answer is understandable without seeing internal schema;
- compact answer preserves the same recommendation state and uncertainty as the full output.

### Regression
- no change to canonical leasing/new-purchase behavior without explicit decision record and regression evidence.

---

## 17. Non-goals for v0

Do not build in the first implementation:

- automated Reddit posting;
- autonomous negotiation with sellers/dealers;
- VIN lookup against paid/private databases without an explicit integration decision;
- image-based mechanical diagnosis presented as verified fact;
- repair-cost precision unsupported by inspection/evidence;
- a universal reliability score pretending to replace vehicle condition;
- regulated financial, legal, insurance or safety advice;
- a new opaque LLM score that bypasses the existing glass-box method.

---

## 18. Architectural invariants

The branch must preserve the following project principles:

1. Source evidence remains inspectable.
2. Missing evidence is visible.
3. A model-derived fact cannot verify itself.
4. User preferences are editable and provenance-labelled.
5. Must-haves remain operational gates.
6. Economic cost and financing cash flow remain separate.
7. Purchase residuals remain scenario-based.
8. Recommendations expose falsifiers.
9. A numeric score alone cannot make a candidate decision-ready.
10. New underwriting functionality must not weaken existing QA/reproducibility requirements.

---

## 19. Open method questions

These must be resolved before production implementation:

1. Is `Vehicle_Instance` accepted as a canonical fourth domain entity, or should it be represented as a subtype/condition record?
2. Which condition/history unknowns are hard readiness blockers versus risk penalties?
3. How should repair-risk scenarios be calibrated without creating pseudo-precision?
4. What evidence threshold promotes repeated owner reports into a reusable `COMMUNITY_PATTERN`?
5. How should market-price comparables be normalized for mileage, trim, geography, seller type and time?
6. What budget-resilience rule is appropriate without turning GLASSBOX into personal financial advice?
7. Which external registries/data sources can be legally, reproducibly and openly integrated?
8. How should user-supplied documents/photos be retained, cited and privacy-filtered in a public/open-source workflow?
9. How should recommendation-state calibration be tested against expert reviewers?
10. Which pieces belong in the general engine versus a Denmark-specific adapter?

---

## 20. First reference fixture

The public r/dkbiler first-car case that motivated this branch should be stored as the initial `UNDERWRITE` acceptance fixture, with the following decision facts preserved:

- first-time buyer;
- student;
- Ford Fiesta 1.25 60 Trend;
- 2011;
- 111,000 km;
- seller states timing belt changed in 2019 at 82,000 km;
- negotiated cash price DKK 28,000;
- physical inspection planned within days;
- user asks whether the purchase is sensible and what to inspect.

Expected engine behavior:

- classify as `UNDERWRITE` + `BUY_USED`;
- treat timing-belt replacement as a seller claim until documented;
- identify service/maintenance history, concrete condition and market price as decision-critical research domains;
- avoid treating general Ford/Fiesta anecdotes as equivalent to evidence about this exact 1.25 variant and vehicle instance;
- return an actionable inspection/verification list;
- withhold a strong buy recommendation while decision-critical instance evidence is unresolved.

This fixture is a test of method discipline, not a predetermined verdict on the car.
