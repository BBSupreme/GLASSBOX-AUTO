# Decision Underwriting — Roadmap

## Status

**Branch:** `product/decision-underwriting`  
**Purpose:** isolate exploration and validation of natural-language car decision underwriting before any merge into the canonical product/method.

This roadmap intentionally treats the existing Excel/matrix work as a reference implementation of decision logic, not as the target user experience.

---

## 0. Outcome definition

The target is not “build a Reddit bot”.

The target is:

> A user can provide a natural-language car question or concrete offer, GLASSBOX converts it into an auditable Decision Case, researches the facts that can change the decision, and returns both a compact recommendation and full evidence trace.

Success is measured against real decision cases, not feature count.

---

## Phase 1 — Freeze the method boundary

### Goal

Prevent the underwriting experiment from silently changing canonical leasing/purchase logic.

### Work

- Treat `DECISION_UNDERWRITING_SPEC.md` as exploratory only.
- Record `Vehicle_Instance` as a proposed architecture decision, not an accepted one.
- Import/resolve the existing Acquisition & Purchase P1–P3 blockers before calling purchase underwriting production-ready.
- Identify all canonical invariants inherited from `METHOD.md`, `DECISIONS.md` and `ACQUISITION_PURCHASE_LAYER.md`.
- Define a regression boundary for existing lease/new-purchase outputs.

### Exit criteria

- Method boundary documented.
- No underwriting code can promote purchase support beyond the current canonical readiness state.
- Existing QA baseline is reproducible.

---

## Phase 2 — Build the 50-case acceptance corpus

### Goal

Use real user decisions as the product contract before building UI or automation.

### Work

Create `qa/decision_cases/` with at least 50 cases across:

- used first car;
- cheap ICE;
- used EV;
- new EV;
- family requirements;
- long-distance commuting;
- low annual mileage;
- premium alternatives;
- lease-vs-buy;
- concrete lease offer;
- private seller;
- dealer offer;
- incomplete/conflicting facts.

Start with the r/dkbiler Fiesta case that motivated the branch.

Each fixture should include:

- raw question;
- expected job classification;
- explicit facts;
- expected critical unknowns;
- evidence constraints;
- expected research domains;
- prohibited overclaims;
- minimum safe answer characteristics.

### Evaluation

Do not grade the system on whether it matches community consensus.

Grade it on:
- extraction accuracy;
- evidence discipline;
- critical-unknown identification;
- no fabrication;
- appropriate readiness;
- useful falsifiers/actions.

### Exit criteria

- 50 version-controlled fixtures.
- Fixture schema validated.
- At least 10 cases independently reviewed for expected outputs.

---

## Phase 3 — Decision Case parser

### Goal

Turn messy natural-language questions into inspectable structured state without inventing facts.

### Build

Proposed modules:

```text
engine/intake/
├── classify_job
├── extract_entities
├── extract_user_context
├── extract_requirements
├── resolve_conflicts
└── build_decision_case
```

### Requirements

- support Danish first;
- preserve source text span/provenance for extracted facts where practical;
- label requirements `STATED`, `INFERRED`, `DEFAULT`, `UNKNOWN`;
- maintain conflicts rather than choose silently;
- detect missing fields only when materially relevant to the current job.

### Tests

- deterministic structured fixtures;
- adversarial ambiguity cases;
- typo/colloquial phrasing;
- omitted trim/year/price;
- multiple cars in one prompt;
- explicit correction by user overrides earlier inference.

### Exit criteria

- ≥95% acquisition-mode extraction on unambiguous corpus cases;
- zero known fabricated critical facts in corpus run;
- stated/inferred provenance survives end-to-end.

---

## Phase 4 — Vehicle Instance spike

### Goal

Prove whether `Vehicle_Instance` is required as a first-class domain entity.

### Build only enough to test

Represent 10–15 used-car fixtures where identical model-level data produces different decisions due to:

- service history;
- timing-belt evidence;
- battery SOH;
- rust;
- tyres/brakes;
- accident history;
- inspection results;
- immediate maintenance.

### Falsification question

Can the existing three-entity architecture represent these cases cleanly without contaminating `Vehicle` or overloading `Acquisition_Offer`?

If yes, reject the fourth entity.

If no, promote `Vehicle_Instance` through a formal architecture decision.

### Exit criteria

- written architecture decision with examples and trade-offs;
- mapping/regression tests;
- no ambiguous ownership of instance-vs-offer fields.

---

## Phase 5 — Evidence acquisition & grading

### Goal

Make research auditable and decision-directed.

### Build

Evidence records should preserve:

```text
evidence_id
claim
source_url/reference
source_class
certainty
retrieved_at
published_at/source_date
vehicle/model/instance linkage
supports_or_contradicts
notes
```

### Initial adapters

Prioritize Denmark-relevant, reproducible sources for:

1. manufacturer specifications/service schedules;
2. official recall/registry information where available;
3. independent tests/guides;
4. live market listings/comparables;
5. user-supplied documentation;
6. community reports as low-certainty pattern signals.

### Rules

- community anecdotes cannot verify instance condition;
- seller claims remain explicitly seller claims;
- models cannot cite their own prior output as evidence;
- time-sensitive market evidence carries dates.

### Exit criteria

- all material claims in 20 pilot cases trace to evidence or explicit inference;
- source class and certainty tested independently;
- stale market evidence is detectable.

---

## Phase 6 — Used-car underwriting kernel

### Goal

Produce a defensible provisional decision for one concrete used car.

### Kernel responsibilities

- fit/must-have gates;
- model-level risk context;
- instance history/condition state;
- deal-quality comparison;
- immediate-cost scenarios;
- holding-period economics;
- budget-resilience flag where explicitly supported by user inputs;
- critical unknowns;
- walk-away/falsifier rules;
- readiness state.

### Do not build

- universal “reliability score”;
- exact repair-cost predictions presented as fact;
- hard-coded brand reputations;
- black-box LLM recommendation independent of evidence state.

### Output prototype

```text
STATE: YELLOW
WHY: potentially sensible, but not decision-ready

FOR
- ...

AGAINST / RISK
- ...

VERIFY BEFORE BUYING
1. ...
2. ...

WALK AWAY IF
- ...

RECOMMENDATION FLIPS IF
- ...

EVIDENCE COVERAGE
- ...
```

### Exit criteria

- 20 used-car cases complete end-to-end;
- reviewers can trace every material recommendation driver;
- different instance condition changes decisions without changing model-level facts.

---

## Phase 7 — Market/deal underwriting

### Goal

Answer “is this particular price actually good?” separately from “is this model suitable?”

### Build

Comparable normalization for:

- model/generation;
- engine/battery;
- trim/equipment;
- registration year;
- mileage;
- seller type;
- warranty context;
- geography where material;
- listing date;
- known condition differences.

### Output

Avoid unsupported exact fair-value claims.

Prefer:
- attractive / market-like / expensive bands;
- comparable range;
- normalization notes;
- factors that justify deviation;
- confidence based on comparable count/quality.

### Exit criteria

- adversarial test demonstrates that a cheap-but-bad instance is not promoted solely on price;
- comparable selection is inspectable;
- stale listings cannot dominate current conclusion.

---

## Phase 8 — Acquisition-mode convergence

### Goal

Use one Decision Case to compare `LEASE_NEW`, `BUY_NEW`, and `BUY_USED` when that is genuinely the user’s question.

### Dependency

Blocked until Acquisition & Purchase P1–P3 and economics anchors are resolved.

### Build

- common holding-period assumptions;
- financing/cash-flow view;
- economic-cost view;
- residual scenarios;
- break-even residual;
- flexibility/liquidity factors as approved by method;
- mileage stress scenarios;
- uncertainty sensitivity.

### Exit criteria

- financing cash flow reconciles separately from economic cost;
- principal is never counted as consumed cost;
- residual scenario can visibly flip recommendation;
- no mode is advantaged by missing-cost treatment.

---

## Phase 9 — Natural-language answer renderer

### Goal

Make the engine useful in the places users already ask questions.

### Renderers

At minimum:

- `full_audit` — complete trace;
- `compact_forum` — approximately 200–400 words;
- `checklist` — inspection/actions only;
- `comparison_summary` — two/few candidates.

### Compact forum contract

Must contain:
- clear provisional verdict/readiness;
- strongest reasons for/against;
- critical unknowns;
- actionable next step;
- falsifier/walk-away condition;
- no unsupported precision.

The renderer must not change the underlying recommendation.

### Exit criteria

- human reviewer can compare compact vs full output and find no material contradiction;
- answers are useful without exposing internal schema;
- sources remain accessible.

---

## Phase 10 — Human-in-the-loop public pilot

### Goal

Validate usefulness before automation.

### Pilot pattern

Manual flow:

```text
public/user car question
→ run through GLASSBOX
→ human reviews evidence/recommendation
→ publish/share compact answer
→ collect corrections and missing evidence
→ update case
```

### Measure

- did the user provide new decision-critical facts after the answer?;
- did the recommendation change?;
- which evidence types were most useful?;
- which questions repeatedly recur?;
- where did the system over/under-research?;
- did users understand `YELLOW`/`UNKNOWN` rather than read it as a rejection?;
- could community corrections be incorporated without contaminating verified facts?

### Exit criteria

- 20+ externally realistic pilot cases;
- all corrections trace to changed evidence/state;
- no critical systematic overclaim remains open.

---

## Phase 11 — Product surface

### Goal

Only after the engine survives real cases, build the simplest useful interface.

### Recommended v1 interface

One primary input:

> **Paste your car question or listing**

Optional progressive disclosure:
- expected annual km;
- holding period;
- household/space needs;
- budget/cash constraint;
- must-haves;
- acquisition preferences.

Then show:

1. **What I understood** — editable facts/assumptions;
2. **Decision state**;
3. **Reasons**;
4. **Critical unknowns**;
5. **What to verify next**;
6. **Sources**;
7. **Full glass-box trace**.

Do not begin with a large matrix or weighting form.

### Exit criteria

- novice can get to a useful case without understanding the internal model;
- expert can inspect/edit all important assumptions;
- no hidden defaults become mandatory preferences.

---

## Phase 12 — Automation and integrations (later)

Only consider after the manual/product flow is validated.

Possible future adapters:
- share extension / URL import;
- browser extension;
- listing-watch changes;
- marketplace import;
- forum/reddit response assistant;
- inspection report upload;
- service document extraction;
- price-change monitoring.

Automated posting should remain out of scope until moderation, platform rules, source attribution and human-review requirements are explicitly decided.

---

# Delivery sequence

Recommended build order:

```text
1. Method boundary
2. 50-case corpus
3. Intake parser
4. Vehicle_Instance spike
5. Evidence model/adapters
6. Used-car underwriting kernel
7. Market/deal layer
8. Resolve purchase blockers
9. Acquisition-mode convergence
10. Natural-language renderers
11. Human pilot
12. Minimal product UI
13. Integrations/automation
```

The key sequencing principle is:

> **Corpus before interface; evidence before recommendation; method before automation.**

---

# Near-term backlog

## P0 — do next

- [ ] Create `qa/decision_cases/schema.json` or equivalent typed schema.
- [ ] Add the motivating Fiesta case as fixture `DU-001`.
- [ ] Collect 9 additional diverse r/dkbiler/public-style cases for the first 10-case mini corpus.
- [ ] Add expected job/critical-unknown annotations.
- [ ] Write architecture note testing `Vehicle_Instance` against the current three-entity model.
- [ ] Locate/import authoritative Acquisition & Purchase P1–P3 materials.
- [ ] Locate/import economics Floor/Need/Stretch anchors and current QA harness.

## P1 — after mini corpus

- [ ] Implement deterministic Decision Case schema.
- [ ] Prototype natural-language intake against 10 fixtures.
- [ ] Create evidence-record schema.
- [ ] Build one primary-source adapter and one market-comparable adapter.
- [ ] Prototype `YELLOW/GREEN/RED/INSUFFICIENT_DATA` mapping without replacing internal readiness.

## P2 — before public pilot

- [ ] Expand to 50 fixtures.
- [ ] Run adversarial review of instance architecture and evidence promotion rules.
- [ ] Complete used-car kernel.
- [ ] Add compact forum renderer.
- [ ] Establish regression suite proving leasing behavior is unchanged.

---

# Kill criteria / reasons to stop or reshape the track

This branch should not be merged merely because the demo feels useful.

Reconsider the product direction if:

1. natural-language extraction repeatedly requires so much clarification that direct matrix entry is materially better;
2. trustworthy, reproducible market/condition evidence cannot be obtained at useful coverage;
3. `Vehicle_Instance` risk dominates outcomes but cannot be assessed without professional physical inspection, making remote underwriting misleading;
4. users interpret uncertainty/readiness states as definitive mechanical assurance;
5. the compact answer loses the glass-box properties that differentiate the project;
6. maintenance/reliability research cannot be normalized well enough to avoid anecdote-driven brand bias;
7. the additional complexity damages the core lease/purchase model without sufficient decision value.

A valid outcome of the branch is therefore also:

> keep GLASSBOX as a decision-preparation and inspection-planning tool rather than claiming full remote used-car underwriting.

---

# Proposed branch completion decision

At the end of the branch, produce one explicit decision:

### MERGE

The capability demonstrably extends the existing method and meets acceptance criteria.

### MERGE PARTIALLY

Keep useful components such as natural-language intake, Decision Case, evidence provenance or compact rendering, but reject full used-car underwriting.

### DO NOT MERGE

Evidence/condition uncertainty makes the concept misleading or methodologically unsound.

No component becomes canonical solely because it exists on this branch.
