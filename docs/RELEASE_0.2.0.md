# Release Notes — Engine 0.2.0

**Release status:** production candidate pending go-live hardening CI  
**Package:** `glassbox-auto==0.2.0`  
**Scope:** leasing engine + recovered-v3 compatibility

## Release content

Engine 0.2.0 adds explicit historical compatibility without making the workbook the source of truth. It includes:

- Revision A / recovered-v3.2 / reconstructed-v3.2.1 source tracks;
- source-backed historical household economics;
- historical Confidence and tri-state Readiness compatibility;
- separate close-call coverage strategies so PC-01 is not silently reconciled;
- corrected offer freshness, family Dealbreaker and lease-terms gates (PC-07/08/09);
- provenance-preserving composite gates;
- `3.2.1-R` reconstruction manifest and workbook validator;
- fail-closed purchase modes pending source-backed purchase economics.

## Go-live hardening additions

The go-live hardening pass adds:

- classified CI jobs for core, historical compatibility, release integrity and full regression;
- current GitHub Actions runtimes;
- explicit failure summaries rather than undifferentiated `test` failures;
- package compile and `pip check` smoke tests;
- a release-integrity executable that prevents accidental provenance/version drift;
- a production-readiness and incident-response contract.

## Known limitations

1. `3.2.1-R` is a reconstructed compliance artifact, not recovered byte-identical historical v3.2.1.
2. PC-01 remains an explicit source conflict: Revision A specifies weight coverage while recovered v3.2 uses four critical checks for the 95% threshold switch.
3. The raw generated 3.2.1-R XLSX is not yet distributed from GitHub through a byte-safe binary path; its expected hash remains pinned.
4. `BUY_NEW` and `BUY_USED` remain method-blocked pending exact P1-P3 findings and purchase Economics anchors.
5. Market offers are only as current as their evidence/control dates; Engine 0.2.0 is not itself a live scraping service.

## Release acceptance

Release only if the same target commit passes all four CI jobs defined in `.github/workflows/engine-ci.yml`.

A GitHub tag/release should point to that exact green `main` commit. If release creation is performed through a client that cannot publish tags/releases, do not fabricate release state in documentation; preserve these notes as the release payload until the tag/release is created byte-safely.
