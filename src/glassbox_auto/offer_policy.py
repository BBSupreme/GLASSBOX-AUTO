"""Versioned scope and limits for the public offer arithmetic interface.

No scoring/freshness/market-truth policy is implied by this narrow calculator.
"""
SCHEMA_VERSION = "offer-check-request.v1"
RESULT_SCHEMA_VERSION = "offer-check-result.v1"
POLICY_ID = "dk-private-lease.v1"
CANONICALIZATION_ID = "GBX-PYJSON-1"
MAX_OFFERS = 250
MAX_DKK = 10_000_000
MAX_ANNUAL_KM = 200_000
MAX_TERM_MONTHS = 120
LEASE_FIELDS = (
    "term_months", "monthly_payment_count", "annual_km", "upfront_payment_dkk",
    "monthly_payment_dkk", "mandatory_fees_dkk", "fees_upfront_dkk",
    "refundable_deposit_dkk", "monthly_insurance_dkk", "overage_dkk_per_km",
)
MONEY_FIELDS = (
    "upfront_payment_dkk", "monthly_payment_dkk", "mandatory_fees_dkk",
    "fees_upfront_dkk", "refundable_deposit_dkk", "monthly_insurance_dkk",
)
LIMITATIONS = (
    "ENTERED_VALUES_ARE_NOT_VERIFIED",
    "CONFIRM_CURRENT_AVAILABILITY_AND_COMPLETE_TERMS",
    "NO_VEHICLE_RANKING_OR_RECOMMENDATION",
    "INITIAL_NON_MONTHLY_CASH_EXCLUDES_FIRST_REGULAR_PAYMENT",
    "RECURRING_BUDGET_EXCLUDES_UPFRONT_AMORTIZATION_AND_OTHER_RUNNING_COSTS",
    "TOTALS_EXCLUDE_DEPOSIT_INSURANCE_ENERGY_TAX_DAMAGE_AND_OPTIONAL_COSTS",
    "NO_UNDER_MILEAGE_REFUND_OR_IMPUTED_VALUE_ASSUMED",
    "OVERAGE_SCENARIO_DOES_NOT_ESTABLISH_CONTRACT_PERMISSION",
    "REFUNDABLE_DEPOSIT_RETURN_IS_CONDITIONAL",
)
