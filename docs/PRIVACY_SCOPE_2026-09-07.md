# Privacy scope decision — 2026-09-07

Status: owner accepts the known ordinary attribution/car-comparison footprint;
not a blanket privacy clearance or release approval.

## Evidence checked

The inspected baseline commit contains owner attribution and email metadata.
The mounted 8,467-byte historical workbook matches the public Git blob
`4cbf783e2b59ab29c3392df871342c7cfa70500b` exactly. Its one visible sheet contains
historical vehicle/lease/insurance comparisons and approximate driving-frequency
notes. Its ZIP has no hidden sheets, docProps, comment, macro or embedded object
entries; inspected relationships point to ordinary public source links and
internal workbook parts. Nothing in those inspected records establishes
wrongdoing. A personalized workbook label alone does not imply harmful content.

No credentials, account numbers, health information or confidential work records
were found in that workbook inspection. Full Git history, all attachments and
third-party rights have not been certified. Avoid interpreting this as legal
clearance or a promise that every previously public object is harmless.

## Owner decision and limits

Absolute anonymity/restored unlinkability is no longer a project goal. The known
ordinary owner attribution/email and non-sensitive historical car-comparison
context are accepted, so do not rewrite history, relocate the repository, or
block repair work solely to remove that footprint. Prefer no-reply attribution
for future writes where available, without making it a repair dependency.

Continue to exclude secrets/tokens, identifiers/account details, precise
sensitive routines, health information, confidential employer/client records,
other people's personal data, and new private household profiles. Newly found
harmful exposure must be assessed separately. D2 and the private RC1 artifact
boundary remain unchanged. Keep public examples synthetic.

AR-A-01's anonymity-only risk is ACCEPTED_BY_OWNER. AR-A-02's restored-anonymity
objective is superseded by this bounded decision, not proven achieved. Preserve
the original review and this dated disposition. PR #10's anonymity requirements
must be read with this superseding owner decision before implementation.

Proceed: narrow engine repair -> reviewed reduced interface -> controlled pilot.
Neither privacy acceptance nor green candidate CI authorizes production release.

Reference: https://docs.github.com/en/account-and-profile/concepts/email-addresses
