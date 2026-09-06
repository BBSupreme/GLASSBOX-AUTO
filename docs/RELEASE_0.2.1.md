# Engine 0.2.1 — claim/gate alignment

**Date:** 2026-09-06  
**Status:** RELEASE CANDIDATE until merged to `main` and green on the exact merge commit.  
**Base:** Engine 0.2.0 production commit `fcf66232fae0f8a36995217f087a489a837d27c2`.

## Why this patch exists

Engine 0.2.0 exposed two different policies for a decision-critical gate whose evidence is `UNKNOWN`:

- the public generic default blocked eligibility;
- binding Revision A D-V3.25 and recovered Leasingmatrix behavior allow the candidate to remain ranked while preventing READY.

That difference was documented, but the default behavior and the canonical method claim did not align. 0.2.1 makes the binding method the default rather than requiring a compatibility-mode exception.

## Behavior change

Default `evaluate_candidate(...)` semantics from 0.2.1:

- gate `FAIL` → `Eligibility.FAILED` / not rank-eligible;
- decision-critical gate `UNKNOWN` → `Eligibility.ELIGIBLE` but `Readiness.NOT_READY`;
- non-critical gate `UNKNOWN` → does not block eligibility or readiness;
- other blockers such as incomplete economics, unit/type mismatch or no scorable criteria continue to block eligibility as before.

The stricter policy remains available explicitly:

```python
evaluate_candidate(
    vehicle,
    offer,
    profile,
    unknown_gate_blocks_eligibility=True,
)
```

Use that override only when the caller intentionally wants fail-closed ranking. Do not describe it as the Revision A default.

## Release-identity correction

0.2.1 also closes a release-claim gap: `pyproject.toml` had reached 0.2.0 while `glassbox_auto.__version__` still reported 0.1.0. The candidate aligns both on 0.2.1 and makes CI assert both wheel metadata and runtime version. The release-integrity gate now checks their agreement from source metadata as well.

## D2 — reconstructed workbook distribution

The planned public binary import/distribution of `3.2.1-R` is retired. Its manifest, reconstruction record, pinned fingerprint and validator remain historical provenance/compatibility evidence. Do not publish the reconstructed XLSX merely to complete an old distribution task, and do not reuse its hash for the separate private RC1 track.

## Unchanged boundaries

- `BUY_NEW` and `BUY_USED` remain method-blocked.
- PC-01 evidence-weight coverage authority remains explicit and unresolved.
- No historical byte-identical v3.2.1 recovery is claimed.
- The private `3.2.1-RC1` workbook review is separate from this Engine patch.
- Live-market freshness is not implied by an engine release.

## Required evidence before release

1. `contracts / core engine` green on the candidate head.
2. `contracts / recovered v3 compatibility` green on the same head.
3. `release / integrity and wheel smoke` green, including package/runtime 0.2.1 agreement.
4. `regression / full suite` green on the same head.
5. Review the PR diff against D-V3.25 and confirm no compatibility adapter was silently rewritten.
6. After merge, require the same classified CI gates to be green on the exact `main` commit before calling 0.2.1 live.

## Migration note

A caller that depended on Engine 0.2.0's implicit fail-closed treatment of decision-critical `UNKNOWN` must opt into that policy explicitly with `unknown_gate_blocks_eligibility=True`. A caller that intended Revision A behavior should remove any unnecessary explicit `False`; the 0.2.1 default now expresses that contract directly.
