# Version History

## 2025 baseline

A highly individualized 2025 leasing matrix existed before the 2026 rebuild and served as inspiration for personalization and comparison structure. The original workbook is available in the project environment but is not yet committed as a binary source artifact in this repository.

## Leasingmatrix 2026 v2 / v2.1

The 2026 project was rebuilt as a fresh workbook rather than simply extending the 2025 file.

v2.1 became the authoritative interim / Phase-1 baseline before the v3 architecture matured.

## Leasingmatrix 2026 v3

The v3 line introduced/refined:

- editable user weighting;
- explicit gates;
- evidence-aware normalization;
- mileage-fit treatment including unused contracted kilometres;
- family subweights;
- deterministic ranking;
- QA harnesses and independent checks;
- decision-oriented shortlist logic.

### Last reviewed standard-profile result

At the last reviewed v3 state, with approximately 85% data-weight coverage, the top eight were recorded as:

| Rank | Candidate | Score |
|---:|---|---:|
| 1 | Kia EV6 | 9.10 |
| 2 | XPENG G6 | 8.98 |
| 3 | BYD Sealion 7 | 8.90 |
| 4 | Skoda Enyaq 85 | 8.89 |
| 5 | VW ID.4 | 8.72 |
| 6 | Polestar 4 | 8.66 |
| 7 | Hyundai IONIQ 5 | 8.59 |
| 8 | Mercedes-Benz GLB 250+ | 8.50 |

The gap from rank 1 to rank 3 was 0.20, which falls inside the project's falsification / close-call band at sub-95% coverage. These results are historical project-state outputs, not claims about current September 2026 market pricing.

## Revision A - 2026-08-29

Revision A became binding over the v3 handover where they conflict. It locked decisions D-V3.21 through D-V3.30, including Must-have gates, weighting multipliers, close-call thresholds, safety placement, readiness semantics, operational gate definitions, Floor/Need/Stretch utility, QA scope and evidence semantics.

See `DECISIONS.md`.

## Acquisition & Purchase Layer Draft A - 2026-08-30

The project expanded from leasing-only toward a unified acquisition model covering leasing, new purchase and used purchase.

Adversarial review outcome:

- architecture accepted;
- method incomplete;
- implementation blocked pending P1-P3 resolution.

See `ACQUISITION_PURCHASE_LAYER.md`.

## GLASSBOX-AUTO - 2026-09-02

The project moved into a public GitHub repository with an explicit open-source, audit-first mission. During migration, exact missing source artifacts are listed as pending rather than recreated from memory.