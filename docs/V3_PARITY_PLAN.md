# Leasingmatrix v3 Parity Validation Plan

**Branch:** `validation/v3-parity`  
**Base:** Engine 0.1.0 merge `e7cf265c16320b0f911cf2eca1e5b35834fb0ca1`  
**Status:** validation work; not a v3.2.1 parity claim

## 1. Objective

Prove, rather than assume, which historical Leasingmatrix v3 semantics can be reproduced by GLASSBOX-AUTO Engine 0.1.0.

The adapter must keep the generic engine independent from workbook-specific behavior. A historical behavior becomes a compatibility rule only when a recovered source supports it.

## 2. Two source tracks

Parity work distinguishes two explicit tracks.

### `REVISION_A`

Binding method decisions from `HANDOVER_ADDENDUM_v3_RevA` dated 2026-08-29. Where it conflicts with the earlier handover, Revision A wins as method canon.

Confirmed examples:
- Need utility = 8/10;
- label multipliers .5 / 1 / 1.5 / 2 / Must-have 2 + gate;
- close-call threshold 0.20 below 95% weight coverage and 0.15 at/above;
- Must-have creates a decision-critical gate;
- non-critical UNKNOWN affects Confidence rather than Readiness;
- Safety = gate + capped child-protection evidence in Family.

### `RECOVERED_V3_2`

Observed behavior from the recovered later `Leasingmatrix_2026_v3.xlsx`, whose internal Change_Log reaches v3.2, plus its implementation handover.

Confirmed examples:
- Family 30/25/30/15;
- NCAP gate >=5 stars and protocol year >=2020;
- gate FAIL removes eligibility; UNKNOWN may remain ranked;
- expected normal use around 9,000 km/year in the recovered workbook;
- unused contracted km are not monetized in its Economics score;
- Confidence derives from four critical checks;
- the workbook's 95% close-call switch uses that four-check coverage rather than Revision A weight coverage.

`RECOVERED_V3_2` is an observation track, not authority to overwrite a conflicting Revision A rule.

## 3. Conflict registry

| ID | Topic | REVISION_A | RECOVERED_V3_2 | Status |
|---|---|---|---|---|
| PC-01 | 95% close-call coverage | evidence-weight coverage | critical verified checks / 4 | **OPEN** — do not reconcile until later authoritative evidence |
| PC-02 | Readiness | decision-critical UNKNOWN + close-call/freshness semantics | observed READY / NEARLY READY / NOT READY from critical-open count + expiry | **TRACK SEPARATELY** |
| PC-03 | Confidence | non-critical gaps reduce Confidence | HIGH/MEDIUM/LOW derived from 4 critical checks | **TRACK SEPARATELY** |
| PC-04 | Economics scope | method-level economics dimension | observed household monthly cost includes lease, energy, insurance, parking, tax/wear reserve, over-km | **ADAPTER REQUIRED** |
| PC-05 | Offer freshness | weekly shortlist checks; STALE caps Confidence/Readiness, EXPIRED #1 -> NOT READY | workbook has ACTIVE/STALE/EXPIRED behavior | **ADAPTER REQUIRED** |
| PC-06 | Composite gates | gates must be operationally defined | NCAP, family test and lease terms are composite checks | **DERIVE ATTRIBUTES + LINEAGE** |

## 4. Parity levels

### L0 — Constants/schema
Recovered constants, labels, anchors, dimensions and gate definitions are represented without ambiguity.

### L1 — Criterion/gate
Known raw observations produce the same PASS/FAIL/UNKNOWN states and same utility values.

### L2 — Candidate score
Known candidate inputs produce the same dimension scores and total score within an explicitly declared numeric tolerance.

### L3 — Decision surface
Known candidate sets produce the same eligibility, ranking, close-call, Confidence and Readiness for a specified source track.

### L4 — Exact historical fixture
A clean clone runs an exact recovered workbook/harness fixture and reconciles every expected output. `v3.2.1-parity-verified` is reserved for this level using the actual v3.2.1 artifact.

Current target is **L0–L3 for recovered v3/v3.2 evidence**. L4/v3.2.1 remains blocked.

## 5. Fixture contract

Every fixture must declare:

- `source_track`;
- source artifact/fingerprint;
- input values and evidence state;
- expected utility/gate/dimension/score/rank outputs;
- tolerance, if numeric;
- known conflicts deliberately excluded from the assertion.

No fixture may silently mix `REVISION_A` and `RECOVERED_V3_2` semantics.

## 6. Adapter architecture

Historical compatibility lives under `glassbox_auto.compat`, not in generic scoring primitives unless a rule is genuinely generic.

The adapter may:
- publish source-backed constants;
- derive auditable composite attributes with evidence lineage;
- calculate historical Confidence/Readiness surfaces;
- calculate historical household Economics from explicit inputs;
- select an explicitly named coverage strategy.

The adapter may not:
- change generic Engine 0.1.0 defaults merely to imitate a workbook;
- resolve PC-01 by choosing whichever rule makes scores match;
- label inferred data VERIFIED;
- enable purchase modes.

## 7. Acceptance criteria for this branch

1. source-track types and recovered constants are tested;
2. both close-call coverage strategies are independently reproducible;
3. recovered-v3 critical-four Confidence is reproducible;
4. historical Readiness logic is implemented only where operationally supported;
5. a source-backed household Economics adapter is added with formula fixtures;
6. composite gate derivations preserve lineage;
7. parity report lists MATCH / DIFFERENCE / UNRESOLVED rather than hiding discrepancies;
8. CI and adversarial review pass before any merge.

## 8. Explicit non-goals

- claiming v3.2.1 parity without its exact fixture;
- rebuilding Excel as the source of truth;
- live market refresh;
- purchase/new-buy/used-buy method implementation.
