# Public & model-neutral agent readiness — v0.2 review amendment

Date: 2026-09-07. Status: REVIEW CANDIDATE; not implementation or launch approval.
Parent: `SPEC_PUBLIC_AGENT_READINESS_v0.1.md` at `1c6cbd0f57383fc9ed6bc8fbb61371abf009ee7e`.
Basis: the PR #10 adversarial review, the proposed local v0.2 amendment, and the subsequent bounded owner privacy decision recorded in PR #14's `docs/PRIVACY_SCOPE_2026-09-07.md`.

This document supersedes conflicting v0.1 requirements for the proposed next implementation. Preserve v0.1 and its attack plan as historical review inputs. New designs below remain subject to separate review; a spec merge does not claim that code, fixtures or provider tests exist.

## 1. Product and capability boundary

Retain: user -> agent -> structured request -> deterministic engine -> result -> explanation.

A supported assistant must have repository-read, local-file and Python/process-execution capabilities, including access to the pinned dependencies. It prepares confirmed preferences and source-linked private-leasing offers, executes the pinned engine, and explains results for the disclosed candidate set. Reading a URL alone does not establish execution.

Without execution capabilities, the assistant may gather or explain inputs but must label its work UNEXECUTED. It must not emit a canonical result or invent substitute scoring. Cross-provider prose and browsing results need not match; identical validated inputs and pinned code/policy must produce the same decision payload.

## 2. Privacy disposition — changed by the owner

Absolute anonymity/restored unlinkability is no longer a project requirement. Ordinary owner attribution/email and the inspected non-sensitive historical car-comparison context are accepted. Do not rewrite history, relocate the repo, or block repairs solely to remove that footprint. Prefer no-reply metadata where practicable, but it is not a repair dependency.

This supersedes the anonymity-only PRIV-00/PRIV-02 requirements in the earlier amendment and the corresponding portions of v0.1 Gate 0. It is acceptance of a bounded risk, not proof of anonymization or blanket privacy clearance.

Secrets, credentials, account/identity numbers, health information, confidential employer/client records, other people's personal data and new private household profiles remain excluded from public sources, examples, logs and reports. Keep synthetic public fixtures. Assess any newly discovered sensitive exposure separately; destructive remediation requires separate authorization. D2 and the private RC1 artifact boundary are unchanged. Keep a dated inventory of inspected surfaces and remaining limitations; do not publish the identifiers being removed.

## 3. Normative authority and execution authority

Normative authority: approved dated decisions and the declared method-policy version define intended behavior. Schemas, examples and prompts must conform.

Execution authority: only the selected pinned engine calculates scores, economic metrics, gates, readiness and ranking. A material method/code conflict blocks the affected recommendation and yields a reproducible finding. Neither silently treating a bug as authoritative nor substituting LLM arithmetic is allowed. Historical compatibility remains explicitly labeled; PC-01 is not silently resolved here.

## 4. Minimum supported implementation

Use two public JSON Schema Draft 2020-12 files with local reusable `$defs`:

- `schemas/evaluation-request.v1.schema.json`
- `schemas/evaluation-result.v1.schema.json`

Add one offline CLI, one small engine-owned policy module, AGENTS.md/README entry points, and the parent's three synthetic golden examples: family-lease, low-mileage-lease and evidence-gap. Embed the research record in the request rather than creating six separately versioned documents or provider SDK infrastructure.

Proposed command remains `python -m glassbox_auto.cli evaluate --request request.json --output result.json`.

Input pipeline: bounded strict JSON parse -> structural schema validation -> semantic IDs/units/references/policy validation -> resolved-profile confirmation check -> shared engine-owned policy -> evaluate_candidate/rank_candidates -> finite output checks -> canonical serialization -> atomic output.

The CLI must not reimplement the mathematics. Provider-specific code may differ only in transport/tool invocation, not method rules. The evaluator does not fetch URLs or remote schemas.

## 5. User intent and policy integrity

Each decision-relevant setting records origin: user-stated, approved default, or explicit normalization. Present the resolved mileage policy, active/excluded weights, Must-haves, thresholds, evidence requirements, anchors and strict-UNKNOWN mode before a decision-grade run.

A material profile or method-policy change changes its fingerprint and invalidates prior confirmation. Keep the confirmation evidence in the actual user interaction; a freely supplied `confirmed: true` or self-reported hash is not authentication. The local MVP need not implement identity signatures, but must not claim malicious-agent-proof consent. The agent test must inspect the interaction, not just JSON.

Approved default profiles belong to the policy module and have versioned provenance. Agents cannot invent anchors, relax required gates or call an advanced custom profile the standard profile. The exact public preset/field mapping and freshness parameters must be approved before a current-market decision-grade pilot. They are not supplied by this amendment, and neither the legacy workbook nor a plausible model guess may silently fill the gap. Synthetic fixed-input testing may use explicitly specified fixture profiles in the meantime.

## 6. Evidence and current-market claims

A URL/date/hash is a traceability aid, not proof that a fact is true. Decision-relevant observations retain claim, value, unit, evidence grade/kind, source locator, matched variant/generation, observation/retrieval dates, validity where stated, and derived lineage. Price publication and independently measured real-world range have different evidence requirements.

Use request assessment time, not the evaluator's live clock. A freshly retrieved expired offer stays expired. Malformed/future observation dates fail validation or the approved policy. Undated evidence never establishes guaranteed validity. Conflicts require a recorded disposition, not silent cherry-picking. Current-market runs require the approved shared freshness/terms policy; a generic low-level READY result is not itself current-offer verification.

Research scope, exclusions, discovery rule and limitations are recorded before ranking-based claims. Say best among the evaluated candidates unless a defined market-coverage protocol was actually executed. Synthetic fixtures declare SYNTHETIC and cannot support live price recommendations.

## 7. Deterministic payload versus runtime envelope

The decision payload includes engine/code/policy/schema identity, request/profile fingerprints, candidate identities, scores, weights/utilities, gates, eligibility/readiness, close calls, economics, coverage, warnings and evidence references.

Keep executed_at, provider identity, duration and tool metadata in a separate optional runtime envelope. Changing the execution clock must not change the decision fingerprint; changing assessment time, confirmed profile or evidence may.

Canonicalization must be named and versioned and implemented once by the package. Before implementation approval, specify finite-number rendering, Unicode handling, key ordering and which arrays are semantic sequences versus ID-indexed sets. Distinguish raw request hash from normalized request hash and result hash. No RFC 8785 or universal cross-language canonicalization claim follows from sorted keys alone. The initial claim may be limited to the pinned Python package/runtime matrix, with exact frozen-request results compared under that declared serializer.

## 8. Strict validation and safe failure

Reject duplicate JSON object keys before they are overwritten, NaN/Infinity, numeric strings where numbers are required, unsupported versions, unknown policy fields and excessive inputs. Date-time format must be asserted, not merely annotated. Validate namespace and composite-ID uniqueness, references/joins, units, currency and allowed acquisition mode after schema validation.

Retain proposed exit codes: 0 evaluation completed (not necessarily READY); 2 invalid input; 3 blocked acquisition method; 4 internal invariant/integrity failure; 5 no evaluable candidates; 6 currency incompatibility. Define deterministic precedence before code approval; schema-valid unsupported purchase requests must not be silently relabeled. Never publish a success-shaped output for a failed run.

Write output atomically, refuse input/output path aliasing, and prevent a stale result being mistaken for a successful new run. Treat external source notes as inert text, not eval/import/shell instructions. Use local-only schema resolution and bounded least-privilege workspaces; no automatic request/profile upload to public issues or CI.

## 9. Repair prerequisite and independent review

PR #14 addresses core prerequisites #11–#13: inclusive score gaps, unambiguous candidate identities/duplicate rejection, and finite arithmetic/results. Integrate only the reviewed accepted repair; preserve exact/adjacent falsifiers and all original engine gates. Do not wait for PC-01, private workbook replay or purchase economics to repair existing defects.

A separate code-review runner is distinct from the coordinating builder, but one provider reviewing code does not certify cross-provider user journeys. Record review identity, exact SHA, findings and evidence actually available. Do not turn a queued/running job, an unreported test count or a self-review into approval.

## 10. Pilot sequence and claim boundaries

Stage A: ten controlled cases with frozen, synthetic or explicitly historical/non-actionable evidence. Exercise confirmed intent, actual execution and correct explanation in one demonstrably capable environment. An honest block is a passing outcome when the case is intentionally underspecified or unsupported.

Stage B: after approved presets/freshness parameters and Stage A, repeat applicable cases with current evidence and source records. This tests research/normalization separately from deterministic mathematics.

Keep every attempt, not just successful retries. Record clarification rounds, execution command/exit code, actual code/policy/schema version, request/result and usability observations. Additional clarification is preferable to fabrication. Synthetic engine tests are not completed human usability tests.

The ten-case design is in `AGENT_PILOT_CASES_v0.1.json`; status is PLANNED, with no invented outputs. Begin with one environment, but advertise only configurations that have actual recorded conformance. The parent's three-provider report remains a gate for a broad three-provider compatibility claim; a one-environment pilot is not that claim.

A reviewer/no-finding result is not a cryptographic proof of execution or general immunity to prompt injection. Retained tool evidence plus independent recomputation is the initial verification method, not a new hosted attestation service.

## 11. Acceptance deltas

| ID | Required evidence |
|---|---|
| PRIV-SCOPE | Bounded owner acceptance applied; prohibited sensitive categories remain excluded; no restored-anonymity claim. |
| CORE-01/02/03 | Reviewed fixes for #11–#13; original and adjacent falsifiers plus full CI/runtime matrix on accepted source. |
| AUTH-01 | Material method/code conflicts block the affected claim without manual replacement scoring. |
| PROF-01 | Actual confirmation trace; material changes invalidate confirmation and fingerprints. |
| POLICY-01 | Approved preset/field mapping and explicit freshness/terms parameters before current-market pilot. |
| EVD-01 | Expired/undated/future/wrong-scope/conflicting sources follow the declared shared policy. |
| DET-01/02 | Fixed assessment time, separate runtime metadata, named serializer and declared hash/ordering semantics tested. |
| VAL-01 | Strict parser, asserted dates, semantic uniqueness/reference/unit/policy checks. |
| IO-01/SEC-01 | Bounded atomic output, no stale-success substitution, no input-provided code/network/schema fetching. |
| CAP-01/RUN-01 | Read-only environments return UNEXECUTED; actual command evidence and recomputation support execution claims. |
| PILOT-01 | All ten frozen cases run and are correctly blocked or evaluated; user-journey observations separately recorded. |
| XMOD-01 | Actual conformance evidence for every specifically advertised provider/model/tool configuration. |

All 20 original implementation falsifiers remain applicable except anonymity-only expectations superseded by the owner. Numerical tolerance does not redefine gates; unknowns are not failures; purchase economics stays blocked.

## 12. Change log and implementation holds

v0.1 -> v0.2: split normative/execution authority; reduce six schemas to two; add confirmed-profile integrity; operationalize evidence/execution limits; separate assessment/runtime time; require strict semantic validation and output isolation; sequence frozen/current-evidence pilots; apply bounded attribution acceptance instead of an anonymity rewrite.

This amendment closes no engine issue and invents no provider certification. Remaining design decisions to settle in review are named serializer details, validation-error precedence/resource limits, exact public preset/field mapping and freshness parameters. These must not be left to an LLM at run time. Approval may authorize the fixed-input prototype before current-market features, with those limitations explicit.

Next gate: separate adversarial review of this amendment and pilot matrix, then a bounded implementation PR. Do not merge the specification as evidence that implementation is complete.
