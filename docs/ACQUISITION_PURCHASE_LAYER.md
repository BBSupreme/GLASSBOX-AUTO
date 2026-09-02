# Acquisition & Purchase Layer

## Status

**Architecture: accepted**  
**Method: blocked pending unresolved items**

This document preserves the adversarial-review outcome of the first Acquisition & Purchase Layer draft rather than treating the draft as implementation-ready.

## What survives

The following should remain intact:

### 1. Three-entity separation

- `Vehicle`
- `Acquisition_Offer`
- `Decision_Candidate`

This allows one vehicle to appear under multiple market offers and acquisition modes without duplicating or contaminating the stable vehicle record.

### 2. Principal is not economic cost

Loan principal is a cash-flow item that builds equity. It must not be counted as consumed economic cost in the same way as depreciation, interest, fees or transaction costs.

### 3. Residual values are scenarios

Purchase economics must not rely on one unsupported residual-value point estimate. At minimum, model a scenario range and expose the assumptions.

### 4. Break-even residual is mandatory

Lease-vs-buy outputs should show the residual value at which the preferred acquisition mode changes. This is a falsifier, not merely an extra statistic.

## Why Draft A was blocked

The review concluded that the architecture was sound but the method was incomplete. Two factors likely to determine lease-vs-buy outcomes were absent, and a third was represented in a way that could bias the conclusion.

The exact original P1-P3 wording and anchor values are not reconstructed here because the authoritative source artifacts are not yet present in this repository. They must be imported from the original review/build package before implementation status changes.

## Implementation rule

Do not treat purchase-mode support as production-ready until:

1. the original P1-P3 findings are imported and resolved;
2. the economics anchors are imported and tested;
3. the purchase QA harness passes;
4. residual scenarios and break-even residuals are visible to the user;
5. financing cash flow and economic cost reconcile independently.

## Intended acquisition modes

```text
LEASE_NEW
BUY_NEW
BUY_USED
```

The long-term objective is one decision surface across all three modes, not separate isolated calculators.