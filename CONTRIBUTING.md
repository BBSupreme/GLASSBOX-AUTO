# Contributing to GLASSBOX-AUTO

Contributions are welcome when they make the decision system more transparent, correct, reproducible or useful.

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