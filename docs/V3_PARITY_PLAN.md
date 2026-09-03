# Leasingmatrix v3 Parity Validation Plan

**Branch:** `validation/v3-parity`  
**Base:** Engine 0.1.0 merge `e7cf265c16320b0f911cf2eca1e5b35834fb0ca1`  
**Status:** validation work; reconstructed v3.2.1 fixture available, historical v3.2.1 parity not claimed

## 1. Objective

Prove, rather than assume, which historical Leasingmatrix v3 semantics can be reproduced by GLASSBOX-AUTO.

The adapter must keep the generic engine independent from workbook-specific behavior. A historical behavior becomes a compatibility rule only when a recovered source supports it. A generated reconstruction is a separate source track and never silently becomes recovered history.

## 2. Three explicit source tracks

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

### `RECONSTRUCTED_V3_2_1`

Controlled generated fixture `fixtures/v3/Leasingmatrix_2026_v3.2.1_RECONSTRUCTED.xlsx`, built from recovered v3.2 and Revision A after the historical v3.2.1 artifact could not be found.

It contains the compliance fixes for PC-07, PC-08 and PC-09 and is labelled `3.2.1-R`. Its expected SHA-256 is `db5d2e8b6429df4229911f6459140ff8d36d8b258609be15a905d4487fc9b972`.

This track may demonstrate reproducible reconstruction. It may not be described as recovered history or as bit-for-bit v3.2.1 parity.

## 3. Conflict / difference registry

| ID | Topic | REVISION_A / intended contract | RECOVERED_V3_2 observation | Status |
|---|---|---|---|---|
| PC-01 | 95% close-call coverage | evidence-weight coverage | critical verified checks / 4 | **OPEN** — reconstruction does not guess later historical behavior |
| PC-02 | Readiness | decision-critical UNKNOWN + close-call/freshness semantics | observed READY / NEARLY READY / NOT READY from critical-open count + expiry | **TRACK SEPARATELY** |
| PC-03 | Confidence | non-critical gaps reduce Confidence | HIGH/MEDIUM/LOW derived from 4 critical checks | **TRACK SEPARATELY** |
| PC-04 | Economics scope | method-level economics dimension | observed household monthly cost includes lease, energy, insurance, parking, tax/wear reserve, over-km | **ADAPTER IMPLEMENTED / FIXTURE PRESENT** |
| PC-05 | Offer freshness | weekly shortlist checks; STALE caps Confidence/Readiness, EXPIRED #1 -> NOT READY | workbook has ACTIVE/STALE/EXPIRED behavior | **ADAPTER IMPLEMENTED** |
| PC-06 | Composite gates | gates must be operationally defined | NCAP, family test and lease terms are composite checks | **ADAPTER IMPLEMENTED; QA REQUIRED** |
| PC-07 | ACTIVE offer whose `Gyldig til` has passed | expired offer must not remain decision-eligible; implementation handover reports EXPIRED -> INELIGIBLE | `Offers_Data!Z` becomes `EXPIRED`, but recovered `Scoring_Engine!X` returns `PASS` for ACTIVE+EXPIRED | **DIFFERENCE; fixed in 3.2.1-R, observed-v3.2 behavior retained for parity** |
| PC-08 | Family-test Dealbreaker | `Dealbreaker? = YES` must fail the family gate | Dealbreaker is row 25, but recovered `Scoring_Engine!Y` reads row 26 (`Dato`) | **DIFFERENCE; fixed in 3.2.1-R, observed-v3.2 behavior retained for parity** |
| PC-09 | Acceptable leasing terms | operational gate requires maximum/actual binding, minimum price, termination and return evidence | recovered `Scoring_Engine!Z` passes solely when minimum price > 0 | **DIFFERENCE; fixed in 3.2.1-R, observed-v3.2 behavior retained for parity** |

### Formula evidence

PC-07 recovered formulas imply ACTIVE + elapsed `Gyldig til` -> freshness `EXPIRED` -> gate `PASS`, because the ACTIVE branch tests only `STALE`.

PC-08 recovered `PRØVEKØRSEL` labels `Dealbreaker?` on row 25 and `Dato` on row 26, while `Scoring_Engine!Y` checks row 26 for `YES`.

PC-09 recovered `Scoring_Engine!Z` is equivalent to `IF(minimum_price>0, PASS, UNKNOWN)`, which does not operationalize the remaining required lease-term evidence.

## 4. Parity levels

### L0 — Constants/schema
Recovered constants, labels, anchors, dimensions and gate definitions are represented without ambiguity.

### L1 — Criterion/gate
Known raw observations produce the same PASS/FAIL/UNKNOWN states and same utility values for an explicitly named source track.

### L2 — Candidate score
Known candidate inputs produce the same dimension scores and total score within an explicitly declared numeric tolerance.

### L3 — Decision surface
Known candidate sets produce the same eligibility, ranking, close-call, Confidence and Readiness for a specified source track.

### L4 — Exact historical fixture
A clean clone runs the exact historical workbook/harness fixture and reconciles every expected output. `v3.2.1-parity-verified` remains reserved for an actual recovered historical v3.2.1 artifact.

The reconstructed `3.2.1-R` fixture does **not** satisfy L4 historical parity by definition.

## 5. Fixture contract

Every fixture must declare:

- `source_track`;
- source artifact/fingerprint;
- input values and evidence state;
- expected utility/gate/dimension/score/rank outputs;
- tolerance, if numeric;
- known conflicts deliberately excluded from the assertion.

No fixture may silently mix `REVISION_A`, `RECOVERED_V3_2` and `RECONSTRUCTED_V3_2_1` semantics.

## 6. Adapter architecture

Historical compatibility lives under `glassbox_auto.compat`, not in generic scoring primitives unless a rule is genuinely generic.

The adapter may:
- publish source-backed constants;
- derive auditable composite attributes with evidence lineage;
- calculate historical Confidence/Readiness surfaces;
- calculate historical household Economics from explicit inputs;
- select an explicitly named coverage strategy;
- expose observed-workbook behavior beside a canonical correction when a regression itself is part of the parity evidence;
- validate a generated workbook fixture against a pinned fingerprint.

The adapter may not:
- change generic engine defaults merely to imitate a workbook;
- resolve PC-01 by choosing whichever rule makes scores match;
- turn PC-07, PC-08 or PC-09 into canonical historical behavior;
- label inferred data VERIFIED;
- enable purchase modes.

## 7. Acceptance criteria for this branch

1. source-track types and recovered constants are tested;
2. both close-call coverage strategies are independently reproducible;
3. recovered-v3 critical-four Confidence is reproducible;
4. historical Readiness logic is implemented only where operationally supported;
5. source-backed household Economics adapter has formula fixtures;
6. composite gate derivations preserve lineage and fail closed on incomplete/invalid data;
7. PC-07/08/09 reproduce observed v3.2 behavior and separately test corrected canonical behavior;
8. CI fingerprints and opens the reconstructed XLSX and verifies its patched formula surfaces;
9. parity report lists MATCH / DIFFERENCE / UNRESOLVED rather than hiding discrepancies;
10. CI and adversarial review pass before merge/version bump.

## 8. Explicit non-goals

- claiming historical v3.2.1 parity without its exact artifact;
- rebuilding Excel as the source of truth;
- live market refresh;
- purchase/new-buy/used-buy method implementation.
