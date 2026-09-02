from __future__ import annotations

from .models import AcquisitionMode, AcquisitionOffer, UserProfile


class PurchaseMethodBlockedError(RuntimeError):
    pass


def lease_economics(offer: AcquisitionOffer, profile: UserProfile) -> dict[str, float]:
    if offer.mode != AcquisitionMode.LEASE_NEW:
        raise PurchaseMethodBlockedError(
            "Purchase economics are blocked until original P1-P3 findings and economics anchors are recovered."
        )
    if offer.term_months is None:
        raise ValueError("Lease offer requires term_months")

    base_cash_cost = (
        float(offer.upfront_payment)
        + float(offer.recurring_payment) * offer.term_months
        + float(offer.mandatory_fees)
    )

    overage_cost = 0.0
    unused_km_value_loss = 0.0
    expected_total_km = 0.0
    contracted_total_km = 0.0

    if profile.expected_annual_km is not None and offer.annual_km is not None:
        years = offer.term_months / 12.0
        expected_total_km = profile.expected_annual_km * years
        contracted_total_km = offer.annual_km * years
        delta = expected_total_km - contracted_total_km
        if delta > 0 and offer.overage_cost_per_km is not None:
            overage_cost = delta * offer.overage_cost_per_km
        elif delta < 0 and profile.unused_km_value_per_km is not None:
            unused_km_value_loss = (-delta) * profile.unused_km_value_per_km

    total_adjusted_cost = base_cash_cost + overage_cost + unused_km_value_loss
    return {
        "base_cash_cost": base_cash_cost,
        "overage_cost": overage_cost,
        "unused_km_value_loss": unused_km_value_loss,
        "expected_total_km": expected_total_km,
        "contracted_total_km": contracted_total_km,
        "total_adjusted_cost": total_adjusted_cost,
    }
