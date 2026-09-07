# SPEC — Public & Model-Neutral Agent Readiness v0.1

**Status:** REVIEW REQUIRED  
**Date:** 2026-09-07  
**Base:** Engine 0.2.1 on `main` at `55e82c378f94e0ea1b6481b405c6cb7053f6b9f8`  
**Purpose:** Make GLASSBOX-AUTO safe to share publicly and reliably usable by multiple AI models without allowing the model to redefine the decision method.

---

## 1. Product statement

A user should be able to give a capable AI assistant the GLASSBOX-AUTO repository URL plus a natural-language description of their car needs and receive a result produced through the same auditable engine regardless of whether the orchestration model is ChatGPT, Claude, Gemini, or another capable coding/research agent.

The model may interpret, research, normalize and explain. The model must **not** calculate or reinterpret the canonical score, gate, readiness, close-call or economics result when the engine can calculate it.

Target architecture:

```text
User intent
   ↓
LLM / agent
- interviews user
- researches evidence
- classifies uncertainty
- creates schema-valid input
   ↓
GLASSBOX-AUTO deterministic engine
- economics
- weights
- utility
- gates
- evidence coverage
- eligibility
- readiness
- close calls
- ranking
   ↓
Structured result
   ↓
LLM / agent
- explains
- identifies missing evidence
- cites sources
- proposes next checks
```

The model is an **orchestrator and interpreter**. The repository is the method authority. The engine is the calculation authority.

---

## 2. Success definition

The project is public-agent-ready only when all of the following are true:

1. a new user can understand the supported scope from the repository root without reading historical migration material;
2. no personal or household-specific material intended to remain private is reachable in the promoted public Git history;
3. no personally identifying author metadata remains in the promoted public history if anonymity remains a project requirement;
4. an AI agent can discover a single authoritative execution contract from the repository root;
5. natural-language needs can be converted into a versioned, validated user-profile schema;
6. candidate offers and vehicle evidence can be represented in a versioned, provenance-bearing schema;
7. a single documented command produces deterministic machine-readable results;
8. identical structured inputs produce identical engine outputs independent of orchestration model;
9. the agent must expose unknowns, assumptions, evidence grades and readiness rather than filling gaps silently;
10. current-market claims require current evidence and explicit retrieval timestamps;
11. unsupported acquisition modes remain fail-closed;
12. public documentation makes clear what the engine does and what the surrounding AI agent does;
13. all public-agent-readiness tests and the existing Engine 0.2.x production gates pass;
14. an adversarial review returns RELEASE rather than FIX FIRST or BLOCKED.

---

## 3. Non-goals

This version does **not** require:

- a hosted consumer website;
- a first-party live scraping service;
- autonomous purchase execution;
- new/used purchase economics;
- historical byte-identical workbook reproduction;
- RC1 workbook release;
- identical prose between different LLMs;
- identical evidence discovery when different models have different browsing/search access.

The determinism requirement applies to the **engine result for identical structured inputs**, not to prose generation or external search coverage.

---

## 4. Binding invariants

### I-01 — Engine owns decision mathematics
No agent prompt, adapter, frontend or example may independently recreate scoring, weighting, gate, readiness, close-call or economics formulas when the canonical engine exposes that behavior.

### I-02 — Same input, same engine result
For a fixed Engine version and byte-identical structured input bundle, all orchestrators must receive the same canonical engine result.

### I-03 — Unknown is not failure
Decision-critical `UNKNOWN` remains rank-eligible but `NOT_READY` under canonical 0.2.1 semantics unless the caller explicitly selects stricter fail-closed eligibility behavior.

### I-04 — Evidence is first-class
Every decision-critical externally sourced value must carry provenance, observation/retrieval date, evidence grade and source identity sufficient for audit.

### I-05 — No silent invention
If the model cannot support a required field, it must emit missing/UNKNOWN or ask the user. It must not synthesize a plausible number simply to complete the schema.

### I-06 — Freshness is explicit
A model may not present historical or undated offer evidence as current. Offer status and freshness are evidence properties, not prose qualifiers.

### I-07 — Private data stays outside the public artifact boundary
Household-specific profiles, private source packages, unpublished workbooks and other personally identifying material must not be committed to public Git.

### I-08 — Unsupported purchase modes stay fail-closed
`BUY_NEW` and `BUY_USED` must remain blocked until their own method/release gates are satisfied.

### I-09 — Model identity cannot change policy
No adapter may contain provider-specific scoring rules such as “Claude interprets Must-have differently” or “Gemini uses a different close-call threshold.”

### I-10 — Release claim is executable
Any README claim that a user can “run GLASSBOX-AUTO with an AI assistant” must be backed by an executable quickstart and a tested schema/CLI path.

---

## 5. Gate 0 — Public privacy and identity hardening

This gate precedes adoption work.

### 5.1 Current known public exposures

The public repository currently contains:

- `data/source-material/2025 leasing matrix.xlsx`, described in-repository as a historical personalized baseline;
- Git commit metadata on current public history containing a personal author email.

Normal deletion in a future commit does not remove either item from existing Git history.

### 5.2 Required outcome

Before broad public promotion:

1. inventory all branches, tags, releases, reachable commits, blobs, issue/PR attachments and source-material files for identity-bearing content;
2. classify each finding: PUBLIC_OK / SANITIZE / REMOVE_FROM_HISTORY / EXTERNAL_REFERENCE_ONLY;
3. replace personalized examples with synthetic or explicitly consented public fixtures;
4. rewrite Git history where required to remove private blobs and identity-bearing commit metadata;
5. rotate/recreate affected branches/tags/releases if history rewrite changes object IDs;
6. verify no stale refs preserve purged blobs;
7. establish pseudonymous/bot author metadata for future commits if anonymity remains required;
8. run a post-rewrite identity scan against names, known personal domains/emails, embedded workbook properties and common Office metadata;
9. document the privacy boundary in `SECURITY.md` or `docs/PUBLIC_PRIVACY.md`;
10. record a new canonical production commit after the rewrite and rerun all release gates.

### 5.3 Privacy acceptance criteria

- **PRIV-01:** no known private/personalized workbook is reachable from promoted public refs;
- **PRIV-02:** no direct personal email remains in promoted commit history if pseudonymity is required;
- **PRIV-03:** Office/PDF metadata scan finds no prohibited identity markers in public binaries;
- **PRIV-04:** examples use synthetic household profiles;
- **PRIV-05:** `.gitignore` blocks private profile/package/binary patterns as intended;
- **PRIV-06:** a documented process exists for contributors to avoid accidental PII/source-file commits.

Failure of any PRIV criterion blocks public launch.

---

## 6. Agent discovery contract

Add root-level `AGENTS.md` as the single machine-oriented entry point.

It must tell any agent, in order:

1. what GLASSBOX-AUTO is;
2. supported acquisition modes;
3. authoritative files and precedence;
4. exact install/run commands;
5. input/output schema locations;
6. evidence rules;
7. prohibited agent behavior;
8. how to handle missing inputs;
9. how to research current offers;
10. how to cite sources;
11. how to interpret eligibility/readiness/close-call;
12. which claims remain unresolved or out of scope;
13. how to produce a user-facing answer without recomputing the engine result.

### 6.1 Authority precedence

Proposed order:

1. released engine code + executable tests;
2. `docs/DECISIONS.md` binding decisions;
3. versioned schemas;
4. `AGENTS.md` orchestration contract;
5. `docs/METHOD.md` explanation;
6. examples and historical compatibility material.

Historical workbook/reconstruction docs must never silently override released canonical engine behavior.

### 6.2 Agent prohibition block

`AGENTS.md` must explicitly prohibit:

- hand-calculating a replacement overall score;
- converting UNKNOWN to PASS/FAIL without evidence;
- fabricating live offers;
- using an expired offer as current;
- changing units without recording normalization;
- inferring VERIFIED evidence from model reasoning;
- presenting an ineligible/NOT_READY candidate as a final recommendation without disclosure;
- enabling purchase economics by prompt instruction;
- using private source-material paths as public user inputs.

---

## 7. Versioned input contracts

Create JSON Schema Draft 2020-12 compatible files:

```text
schemas/
  profile.v1.schema.json
  vehicle.v1.schema.json
  offer.v1.schema.json
  evidence.v1.schema.json
  evaluation-request.v1.schema.json
  evaluation-result.v1.schema.json
```

### 7.1 `profile.v1`

Must represent at minimum:

- profile ID;
- expected annual km;
- optional unused-km value policy;
- currency;
- dimensions and base weights;
- criteria;
- preference labels;
- Must-have designation/gate link;
- Floor / Need / Stretch anchors where applicable;
- units;
- decision-critical flags;
- optional explicit strict-UNKNOWN eligibility override;
- free-text source note for user-stated preferences.

The schema must distinguish **user preference** from **external evidence**.

### 7.2 `vehicle.v1`

Must include:

- stable vehicle ID;
- make/model/variant/generation identity;
- attributes as typed observed values;
- evidence object per externally sourced attribute where relevant.

### 7.3 `offer.v1`

Must include:

- stable offer ID;
- vehicle ID;
- acquisition mode;
- currency;
- term;
- annual km;
- upfront payment;
- recurring payment;
- mandatory fees;
- overage cost where known;
- binding/termination/return evidence where used by gates;
- source URL/reference;
- observed/retrieved timestamp;
- validity/end date where stated;
- freshness/status field derived by code where possible, not guessed by the LLM.

### 7.4 `evidence.v1`

Must distinguish:

- VERIFIED;
- ESTIMATED;
- UNKNOWN;
- DIRECT / DERIVED / MODELED;
- source identity;
- retrieved/observed date;
- lineage for derived values;
- optional quoted/source snippet subject to copyright limits outside the engine core.

### 7.5 Unknown handling

Schemas must support absent/UNKNOWN values without forcing agents to invent placeholders.

Schema validation must reject:

- malformed units;
- impossible negative economics;
- unsupported acquisition modes when evaluation requests claim production support;
- VERIFIED modeled evidence;
- missing IDs/references required for joins;
- ambiguous currency on economic fields.

---

## 8. Canonical CLI

Expose one public command path.

Proposed interface:

```bash
python -m glassbox_auto.cli evaluate \
  --request examples/family-lease/evaluation-request.json \
  --output result.json
```

Optional installed console script after packaging:

```bash
glassbox-auto evaluate --request request.json --output result.json
```

### 8.1 CLI requirements

- deterministic JSON output;
- stable documented exit codes;
- no network calls inside the core evaluation command;
- schema validation before evaluation;
- engine version embedded in result;
- input schema version embedded in result;
- input hash/fingerprint embedded in result;
- reasons, eligibility, readiness, coverage and close-call state returned explicitly;
- no prose-only output as the canonical machine interface;
- optional human-readable formatter may sit above canonical JSON.

### 8.2 Exit codes

Proposed:

- `0` evaluation completed successfully;
- `2` schema/input validation failure;
- `3` unsupported acquisition/method block;
- `4` internal invariant/release-integrity failure;
- `5` no evaluable candidates;
- `6` currency/ranking incompatibility.

Exit codes must not encode recommendation rank.

---

## 9. Evaluation result contract

`evaluation-result.v1` should include:

- engine version;
- schema version;
- evaluation timestamp;
- input fingerprint;
- ranked candidate IDs;
- candidate score where scorable;
- eligibility;
- readiness;
- close-call flag;
- data coverage;
- evidence coverage;
- gate states;
- criterion-level utilities/weights/reasons;
- economics breakdown;
- unresolved/missing decision-critical evidence;
- explicit method-block reasons;
- warnings;
- provenance references linking back to input evidence IDs.

The agent-facing explanation must be generated **from this result**, not from an independent recalculation.

---

## 10. Current-market research contract

Because the engine does not include a first-party live-market ingestion service, agent interoperability requires a documented research boundary.

### 10.1 Agent responsibilities

An agent with browsing/search access may:

- discover candidate models/offers;
- retrieve manufacturer/dealer/independent test evidence;
- normalize source formats into schema-valid evidence;
- note conflicts between sources;
- ask the user for missing preferences;
- rerun the deterministic engine when evidence changes.

### 10.2 Agent must not

- claim complete market coverage unless a defined catalog/search protocol was executed;
- promote marketing/model inference to VERIFIED;
- hide source conflict by choosing the convenient number;
- use stale historical fixtures as current offers;
- fill missing lease terms from “typical” market practice;
- alter the candidate set after seeing scores without recording the selection rule.

### 10.3 Research record

Each evaluation intended to support a real decision should produce or retain a machine-readable research manifest containing:

- query/research date;
- market/geography;
- candidate discovery rule;
- source IDs/URLs;
- retrieval timestamps;
- evidence grades;
- exclusions and reasons;
- known coverage limitations.

This can initially be user-local rather than committed to Git.

---

## 11. Synthetic examples

Add at least three public examples built from synthetic profiles and synthetic or clearly historical/non-actionable offers.

```text
examples/
  family-lease/
  low-mileage-lease/
  evidence-gap/
```

Each example must include:

- `user-request.txt` natural-language request;
- `evaluation-request.json` canonical structured input;
- `expected-result.json` golden engine output;
- `README.md` explaining transformation decisions without exposing private data.

### Required examples

**EX-01 Family lease:** two-child household style requirements, 20,000 km, at least one Must-have.

**EX-02 Low mileage:** demonstrates unused-km assumptions and economic uncertainty.

**EX-03 Evidence gap:** top-scoring candidate has a decision-critical UNKNOWN and therefore remains NOT_READY.

Examples are contract fixtures, not marketing recommendations.

---

## 12. Cross-model interoperability harness

### 12.1 What is tested

The harness must distinguish two layers:

**Layer A — orchestration conformance:** can a model transform the same natural-language request into schema-valid inputs without violating agent rules?

**Layer B — engine determinism:** given identical canonical inputs, does every model/toolchain invoke the same engine version and return the exact same canonical result bytes or normalized JSON structure?

Layer B is mandatory for release. Layer A is an interoperability evaluation and may vary by model.

### 12.2 Minimum model matrix

At release review, execute the same test corpus with at least:

- one OpenAI coding/research-capable model;
- one Anthropic Claude coding/research-capable model;
- one Google Gemini coding/research-capable model.

Provider-specific versions must be recorded in the evaluation report because model behavior changes over time.

### 12.3 Conformance metrics

For each model/case record:

- repo discovery success;
- followed `AGENTS.md` without extra instruction;
- valid schema produced;
- unsupported fields invented? yes/no;
- evidence-grade violations;
- units normalized correctly;
- missing information surfaced;
- engine actually executed;
- canonical result matches golden result for fixed-input phase;
- readiness/eligibility explained correctly;
- citations preserved;
- prohibited manual scoring detected.

### 12.4 Pass standard

For fixed canonical inputs:

- 100% identical canonical engine results across orchestrators;
- 0 prohibited manual-scoring substitutions;
- 0 UNKNOWN→VERIFIED upgrades without source evidence;
- 0 production enablement of blocked purchase modes.

For natural-language-to-schema cases:

- all outputs schema-valid after at most one explicit clarification round;
- deviations in discretionary interpretation must be surfaced rather than hidden;
- any difference that changes a decision-critical gate or active weight requires user confirmation or documented policy.

---

## 13. README public quickstart

After implementation, the root README should contain a short section titled:

## Use GLASSBOX-AUTO with an AI assistant

It should provide one copyable prompt such as:

> Read this repository beginning with `AGENTS.md`. Help me compare current private-leasing options for my needs. First translate my requirements into `profile.v1`; ask me only for decision-critical missing preferences. Then research candidate evidence with sources and retrieval dates, create schema-valid vehicle/offer inputs, run the repository's canonical CLI, and base your recommendation only on the returned engine result. Do not recreate the scoring logic yourself. Show eligibility, readiness, coverage, close calls, assumptions and unresolved evidence before recommending anything.

The prompt is convenience only; `AGENTS.md`, schemas and executable behavior remain authoritative.

---

## 14. CI additions

Add a new classified job rather than mixing agent-contract failures into core-engine tests:

`contracts / public-agent interface`

Required checks:

- JSON schemas parse and validate;
- all examples validate;
- golden examples reproduce exactly;
- CLI exit-code tests;
- CLI deterministic output test;
- package install + CLI smoke test;
- `AGENTS.md` links/paths exist;
- no example contains blocked personal markers;
- no duplicate scoring thresholds/formulas appear in adapter/example code;
- unsupported purchase-mode examples fail closed;
- evidence-grade falsifiers;
- input fingerprint stability.

Existing four Engine gates remain mandatory and unchanged.

---

## 15. Public-release gates

Public/agent readiness requires all of:

### Gate A — Privacy
PRIV-01 through PRIV-06 PASS after any history rewrite.

### Gate B — Engine
Engine production gates green on exact canonical public `main` commit.

### Gate C — Interface
Schemas, CLI, AGENTS.md and synthetic examples all executable from a clean checkout.

### Gate D — Determinism
Golden-input evaluation returns exact expected canonical result.

### Gate E — Cross-model
Minimum three-provider interoperability report completed; no P0/P1 violation.

### Gate F — Claims
README and release copy distinguish:

- engine-calculated result;
- agent-researched evidence;
- market-coverage limitations;
- unsupported purchase modes;
- unresolved PC-01 where still applicable.

### Gate G — Adversarial review
Independent/reviewer pass returns RELEASE.

No gate can be waived silently. A waiver requires a dated documented decision and must narrow the public claim accordingly.

---

## 16. Implementation sequence

### Phase 0 — Privacy hardening

1. full identity/blob/history inventory;
2. determine allowed pseudonymous contributor metadata;
3. replace/remove personalized fixture;
4. history rewrite where required;
5. purge stale refs/tags/releases;
6. clone-clean verification;
7. rerun Engine production CI and establish new canonical main SHA.

Do not build public examples on top of history that is expected to be rewritten.

### Phase 1 — Machine contract

1. `AGENTS.md`;
2. schemas;
3. schema validation package/module;
4. canonical CLI;
5. canonical result serializer;
6. golden synthetic examples.

### Phase 2 — Agent/research contract

1. current-market research rules;
2. research manifest schema;
3. source/evidence mapping guide;
4. user clarification policy;
5. README quickstart.

### Phase 3 — Falsification

1. public-agent CI job;
2. malformed-input tests;
3. prompt-injection/adversarial source tests;
4. cross-model evaluation;
5. privacy scan;
6. adversarial review.

### Phase 4 — Release

1. resolve all P0/P1 findings;
2. merge reviewed implementation;
3. same-commit main CI green;
4. tag/release new public-agent-ready version;
5. publish precise supported-scope statement.

---

## 17. Versioning recommendation

Do not label this a documentation-only patch.

Because this adds a supported public interface, schemas and CLI, use at least a **minor Engine release** after implementation, e.g. `0.3.0`, while keeping existing Engine 0.2.1 semantics stable underneath.

Proposed compatibility contract:

- Engine semantic version identifies executable decision behavior/interface release;
- schema files carry their own `v1`, `v2` compatibility versions;
- `evaluation-result` always records both engine version and schema version.

A future LLM/provider change must not require a new Engine version unless repository code/contracts change.

---

## 18. Open design decisions for adversarial review

**D-AR1 — Privacy rewrite scope:** rewrite only promoted refs, or recreate a clean public repository from a sanitized export? Reviewer must compare auditability vs residual discoverability risk.

**D-AR2 — CLI input granularity:** one combined evaluation-request bundle vs separate profile/vehicle/offer files. Proposed default: combined request with referenced evidence objects for simplest agent interoperability.

**D-AR3 — JSON canonicalization:** define byte-canonical JSON for golden hashes or compare normalized semantic structures. Proposed default: canonical serializer in code, hashes over UTF-8 canonical output.

**D-AR4 — Research manifest:** mandatory for all evaluations or only decisions claiming current-market relevance. Proposed default: mandatory whenever any externally discovered evidence is used.

**D-AR5 — Agent clarification threshold:** when may a model infer a soft preference vs requiring user confirmation? Proposed default: agents may normalize wording but may not invent numeric anchors, Must-haves or decision-critical gates without user confirmation or explicit documented defaults.

**D-AR6 — Public market catalog:** whether a public maintained offer/catalog layer belongs in 0.3.0. Proposed default: no; keep ingestion external and schema-based first to avoid coupling engine release cadence to scraping/data operations.

---

## 19. Definition of done

Public Agent Readiness v0.1 is complete only when:

- privacy Gate 0 is proven against public Git history;
- `AGENTS.md` exists and is executable as a model-neutral contract;
- v1 input/evidence/result schemas exist and are tested;
- canonical CLI exists and runs from clean install;
- at least three synthetic examples reproduce golden outputs;
- fixed canonical inputs yield identical engine results across the three-model test matrix;
- model-generated inputs cannot silently bypass evidence/gate rules;
- all existing Engine gates and new public-agent interface gates are green on the same `main` commit;
- adversarial review is closed with RELEASE;
- public README claims no more than the executable evidence supports.
