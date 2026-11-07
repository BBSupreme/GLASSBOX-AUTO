# Offer checker reliability review — 2026-11-07

An agent separate from the interface builders reviewed and executed the narrow
offer-checker interface. No unresolved P0/P1 transport or packaging finding was
identified in the reviewed implementation. This is a code and runtime review,
not a human usability study or an AI-provider certification.

Reviewed package/schema fingerprint:
`44bbd1f15d58ebb5fb84268a9d19a6c48ae4145b3baffb2f56156662a48d51dd`.
The fingerprint is produced by `offer_check.code_fingerprint()` and covers the
installed Python implementation and JSON schemas. A later code/schema change
requires fresh verification; documentation and synthetic examples are excluded
from that fingerprint.

## Findings and repairs

| Finding | Reproduction | Repair and retained check |
|---|---|---|
| A successful worker exit could promote an empty/unrelated object as a decision; a stale valid result could also be attached to a changed request | Substitute `{}` or an earlier decision for the worker's stdout | Closed result validation plus package/code, request, profile and ordered-input binding; malformed and replayed results now fail with exit 4 |
| Replacing the output parent with a symlink after preflight redirected publication | Rename the checked directory, replace it with a link, then publish | Anchored no-follow directory descriptors and descriptor-relative private temporary files, hard-link publication and cleanup |
| A standards-based JSON Schema validator rejected valid monetary values such as 0.29 | `multipleOf: 0.01` with ordinary binary floats | Schema types/bounds remain portable; exact decimal precision is an explicit semantic check, documented by `x-decimal-places` |
| The initial source distribution included tests but omitted their public fixture files and operating instructions | Inspect the built source archive and attempt to reproduce repository checks | Explicit source manifest includes public JSON fixtures, Markdown instructions and the smoke script |

The independent regression file is
[`tests/test_offer_transport_adversarial.py`](../tests/test_offer_transport_adversarial.py).
It also checks duplicate and escaped-equivalent keys, unsafe/non-finite numbers,
UTF-8 and surrogate handling, Unicode preservation, integer-versus-float hashing,
negative zero, byte/depth/node limits, no-clobber races, private output modes,
hard-link aliases, timeout failure, private error sanitization, schema conformance,
and stable decisions under offer permutations.

## Executed evidence

- The pre-interface suite passed: 270 tests on CPython 3.12.14.
- The complete candidate suite passed: 404 tests on CPython 3.12.14 and 404 on
  CPython 3.13.5, on Linux, without skipped tests.
- The rebuilt source distribution included its fixtures, instructions, smoke
  script and golden tests; all 404 tests passed from the unpacked source archive.
- All three packaged examples and their actual subprocess outputs passed the
  published request/result schemas with `jsonschema==4.26.0` and asserted formats.
- The three complete canonical decision payloads were byte-identical across those
  two Python runtimes. The combined JSON output, including its final newline, had
  SHA-256 `5f2076fd6ff34fc8c6d0c8fcb0b12746918f1de03b09962807ce5b2d66af1342`.
- A wheel built from the source distribution installed into a clean environment
  without dependencies. `scripts/smoke_offer_checker.py` exercised all three
  examples outside the checkout, including confirmation, altered-input rejection,
  transport-format changes, hashes, missing values, mileage scenarios and
  refusal to overwrite an existing result.
- The built wheel's release-integrity command passed against the source metadata;
  historical provenance and the unresolved PC-01 disclosure remained intact.
- An obvious-secret pattern scan of tracked text found no credential/private-key
  patterns. This is not a complete Git-history or privacy certification. Public
  examples remain synthetic; the existing bounded attribution decision is unchanged.

The installed-wheel decision digests were:

| Example | `decision_payload_sha256` |
|---|---|
| Complete | `c751cd58047a296a9a6d926bcad6c82595fca1259569f5905ab4cd5ad6b3f9b1` |
| Incomplete | `9b2c01d0bb25b7382871e58433a140cde80b336057960a03f07289251d3e9566` |
| Over mileage | `014f9ee64594b42e0d3d4ed96656aec0ca927d0242008a57629198f66839a7b8` |

## Limits and release disposition

These checks support the narrow conditional-arithmetic beta. They do not prove
source truth, correct agent extraction, genuine user assent, prompt-injection
immunity, vehicle suitability, market coverage, or compatibility with an AI
provider. The public schemas describe structure; extra engine semantic checks,
including integer-token and decimal-precision requirements, remain authoritative.

Python 3.11/3.14 and the exact promoted commit must pass the repository's CI gates.
This local review does not mark an unmerged branch live. Safe file output uses
POSIX directory-descriptor operations; untested operating systems are not certified.
The separate broad agent-ranking specification and its planned provider pilot
remain outside this release's approval.

References: [interface contract](OFFER_CHECK_CONTRACT_v1.md),
[release gates](PRODUCTION_READINESS.md),
[Python JSON](https://docs.python.org/3/library/json.html),
[Python filesystem APIs](https://docs.python.org/3/library/os.html),
[JSON Schema 2020-12](https://json-schema.org/draft/2020-12).
