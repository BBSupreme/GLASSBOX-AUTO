# Contributing to GLASSBOX-AUTO

Contributions are welcome when they make the decision system more transparent, correct, reproducible or useful.

## Run the project

Use Python 3.11 or newer in an isolated environment. From the repository root:

```bash
python -m pip install -e . pytest==9.1.1
python -m pytest
python -m glassbox_auto.cli --help
```

Follow the [AI quickstart](docs/AI_QUICKSTART.md) for an executed example and the
[offer-check contract](docs/OFFER_CHECK_CONTRACT_v1.md) for exact input semantics.
Prompts, schemas and adapters must not introduce mathematics that disagrees with
the engine. Changes to request semantics or normalization need an explicit
schema/policy version decision and tests at the affected boundaries.

## Report an offer-check problem

Include the commit SHA, Python/package versions, exact command, exit code,
observed result and expected result. Prefer a small synthetic request that
reproduces the issue. State whether you actually ran the CLI; an assistant's
prose answer is not an engine execution trace.

Do not upload a real household request, quote, transcript or result unchanged.
Remove personal names, addresses, customer identifiers, credentials and private
contact details. Public examples and tests must use synthetic data. Keep source
licensing in mind before attaching third-party documents.

Request/result hashes are identifiers, not privacy-preserving anonymization or
proof of user consent. Keep private files outside commits and CI artifacts.

## Contribution principles

### Prefer evidence over assertion

For factual vehicle or offer data, include:

- source URL or source artifact;
- publication/update date where available;
- date accessed;
- evidence grade;
- any transformation or normalization applied.

### Do not silently repair source data

If a source is inconsistent, preserve the raw evidence and document the normalization separately.

### Separate vehicle facts from offers

Stable vehicle attributes belong to `Vehicle`. Commercial terms belong to `Acquisition_Offer`. Comparison outputs belong to `Decision_Candidate`.

### No opaque scoring changes

A scoring change should include:

- rationale;
- affected criteria;
- before/after behavior;
- boundary tests;
- explanation of how the change could alter decisions.

### Gates require operational definitions

Do not add a Must-have or safety gate without defining its required evidence, pass/fail boundary and unknown-data behavior.

## Evidence labels

Use the canonical evidence semantics:

- `VERIFIED`
- `ESTIMATED`
- `UNKNOWN`

Do not upgrade an estimate to VERIFIED simply because it appears plausible.

These are lower-level engine evidence semantics. The public offer-check request
does **not** accept asserted evidence grades: every source assertion remains
unverified. A URL, timestamp or matching hash provides traceability, not truth.

## Pull requests

A useful PR should state:

1. What decision problem it addresses.
2. What changed.
3. Which assumptions changed.
4. What tests were added or run.
5. What could falsify the proposed conclusion.

## Source material and copyright

Do not assume that third-party brochures, reviews, price lists or test data can be relicensed under the repository license. Raw third-party materials should remain clearly identified with original ownership/provenance and should only be included where redistribution is lawful.

## AI-assisted contributions

AI assistance is allowed. The contributor remains responsible for provenance, correctness, licensing and tests. AI-generated claims without traceable evidence should not be merged as factual data.

Follow [AGENTS.md](AGENTS.md). Report the environment and checks actually run;
passing tests or a code review do not certify every AI provider or complete a
human usability pilot. Preserve all known limitations in release claims.
