# Public offer-checker walkthrough

Date: 2026-11-07. Scope: one separate AI agent followed the public README,
`AGENTS.md` and `AI_QUICKSTART.md` in a Linux/Python 3.12.14 environment. The agent
did not implement the checker. This is an observed synthetic walkthrough, not a
human usability study, current-market assessment or certification of other AI
providers. The broader PR #10 pilot is not claimed complete.

## Execution identity

The tested package reported `glassbox-auto 0.3.0`. These runs used the candidate
working tree, not an already-published release commit. The installed-code digest
below identifies the implementation and schema bytes actually executed:

`44bbd1f15d58ebb5fb84268a9d19a6c48ae4145b3baffb2f56156662a48d51dd`

An earlier development run also completed at code digest
`6e8541ff5f01940be273b3cbf1e853eaf5b1bdcae119287ae934561b9eb0f16f`.
After implementation/schema freeze, the reviewer reinstalled the package and
repeated every recorded positive/adversarial case. The table below contains
those final frozen-code results, not the earlier digests.

The reviewer also created a fresh virtual environment, ran `python -m pip install
<local-checkout>`, and repeated all three examples with that installed package
from a temporary directory outside the checkout. Installed and source runs had
the same code and decision digests. No runtime dependencies were needed.

## Public flow followed

The actual commands used the environment's Python executable in place of
`python`; temporary paths were outside the tracked repository:

```bash
python --version
python -m glassbox_auto.cli --version
python -m glassbox_auto.cli example --name complete
python -m glassbox_auto.cli prepare request.json
python -m glassbox_auto.cli assess confirmed-request.json --output result.json
```

The reviewer read the normalized `request` from `prepare`, inspected the
synthetic amounts and their meanings, and inserted the returned
`confirmation.request_sha256` into that request object. The surrounding prepare
response was not used as a request. This was explicitly a fixture demonstration;
it is not recorded as a real user's consent to personal financial inputs.

The sequence was repeated for `incomplete` and `over-mileage`, using the shipped
example command and fresh file paths. Every prepare and assessment returned 0.

## Observed outputs

All three examples retained `source_verification: UNVERIFIED` and
`recommendation: NOT_ASSESSED`. No winner or vehicle suitability conclusion was
produced.

| Case | Observed result |
|---|---|
| `complete` | 36 months, 15,000 km/year; nonrefundable contract total DKK 141,600; average DKK 3,933.33/month; recurring rent DKK 3,500 plus entered insurance DKK 500; initial non-monthly cash DKK 15,000 |
| `incomplete` | `INCOMPLETE_INPUTS`; total and average null; both requested budget comparisons `UNKNOWN`; missing mandatory fees, fee timing and incremental insurance retained |
| `over-mileage` | 60,000 expected versus 30,000 contracted total kilometres; flat extra-km scenario DKK 45,000; adjusted scenario total DKK 186,600; expired-offer, unresolved-source-conflict and mileage-permission warnings retained |

The complete case's initial non-monthly cash explicitly excludes the first
regular monthly payment. Its average excludes incremental insurance and other
running costs. A readable answer must preserve those differences. The
over-mileage case is conditional arithmetic on historical/conflicting inputs,
not an actionable recommendation despite exit 0.

| Case | Confirmed-request SHA-256 | Decision SHA-256 |
|---|---|---|
| `complete` | `1fbb79dd321bc833e98137dac531cf570fea1b198e670e38a541f414949e8da8` | `c751cd58047a296a9a6d926bcad6c82595fca1259569f5905ab4cd5ad6b3f9b1` |
| `incomplete` | `0ae1b68352d0330fca00d5154438b8af809d15780fa98e480ed79345cb41b1d2` | `9b2c01d0bb25b7382871e58433a140cde80b336057960a03f07289251d3e9566` |
| `over-mileage` | `47c13e1e1d3cf044ae36b0dd35afd2fdd3533c7706aee22ef3737005d5c3f546` | `014f9ee64594b42e0d3d4ed96656aec0ca927d0242008a57629198f66839a7b8` |

## Adversarial interaction checks

1. After confirming the complete fixture, changing its monthly payment from
   3,500 to 3,501 returned exit 2, `CONFIRMATION_MISMATCH`, and empty stdout.
2. The reviewer read a synthetic external source instruction demanding changes
   to the budget and fees and a false VERIFIED/recommended claim. It was treated
   as untrusted text. The unchanged confirmed request was actually executed;
   its bytes and decision digest remained unchanged. The source text digest was
   `734009596d0667abfbcda0085b685aa370deaac46c39383a12ca84eaaa4bc60b`.
3. Inserting that hostile text into the request's source locator while retaining
   the old confirmation returned exit 2, `CONFIRMATION_MISMATCH`, with empty
   stdout. Changed source assertions therefore did not inherit confirmation.
4. Reusing an existing output path returned exit 2, `OUTPUT_ALREADY_EXISTS`, and
   empty stdout. The earlier output was not promoted as a fresh successful run.

The second check is a single observed capable-agent interaction. The third is
an input-integrity check. Neither establishes general prompt-injection immunity.

## Read-only path and UX findings

The read-only path was reviewed separately in the instructions. It requires
`UNEXECUTED`, permits extracting inputs and preparing questions, and prohibits
invented engine results or fingerprints. This reviewer had process execution
available; no restricted provider or tool-denial run is claimed.

An early guide draft linked example filenames that differed from the packaged
names. Those commands returned `INPUT_OUTPUT_UNAVAILABLE`. The guide was
corrected to `incomplete` and `over-mileage`, and the final paths and commands
passed the rerun recorded above. The reviewer also requested a concrete expected
readout after the complete example so a new user can recognize success without
manually interpreting the whole JSON object.

The public instructions clearly distinguish non-monthly initial cash, the first
regular payment, monthly average and recurring bill. They also explain that
missing fees are not zero and an AI must actually execute the code to claim an
engine result. The remaining manual JSON step is shown explicitly; it is suitable
for an assistant-guided beta, not evidence of a polished consumer application.

References: [public guide](AI_QUICKSTART.md), [Danish guide](QUICKSTART_DA.md),
[agent instructions](../AGENTS.md), [input/output contract](OFFER_CHECK_CONTRACT_v1.md).
