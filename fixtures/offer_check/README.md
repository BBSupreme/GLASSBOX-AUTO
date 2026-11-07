# Offer-checker deterministic fixtures

These three canonical decision files use only the packaged synthetic inputs.
They are not current market offers, user profiles or proof of source truth.
The complete, incomplete and over-mileage examples exercise known arithmetic,
preserved unknowns and expired/conflicting source assertions respectively.

Every Python 3.11–3.14 CI leg compares the complete canonical decision bytes,
including the installed-code fingerprint, against these same expected files.
The raw transport digest is deliberately outside those bytes.

After an intentional implementation/schema change, inspect the semantic diff,
rerun independent arithmetic/transport checks, and explicitly refresh the fixtures
as part of that reviewed change. A failing golden must not be hidden by an
automatic regeneration step in CI.
