from __future__ import annotations

from typing import Any

from .models import (
    AcquisitionMode,
    AcquisitionOffer,
    Evidence,
    EvidenceGrade,
    EvidenceKind,
    GRADE_RANK,
    ObservedValue,
    UserProfile,
)


class PurchaseMethodBlockedError(RuntimeError):
    pass


def _value(observed: ObservedValue | None) -> float | None:
    if observed is None or observed.value is None:
        return None
    return float(observed.value)


def _minimum_grade(values: list[ObservedValue]) -> EvidenceGrade:
    if not values:
        return EvidenceGrade.UNKNOWN
    return min((v.evidence.grade for v in values), key=lambda g: GRADE_RANK[g])


def _derived_value(
    value: float | None,
    *,
    inputs: list[ObservedValue],
    unit: str,
    method: str,
    max_grade: EvidenceGrade | None = None,
    extra_lineage: tuple[str, ...] = (),
) -> ObservedValue:
    lineage = tuple(dict.fromkeys(
        source
        for source in (*[v.evidence.source for v in inputs if v.evidence.source], *extra_lineage)
        if source
    ))
    if value is None:
        return ObservedValue(
            None,
            Evidence(
                grade=EvidenceGrade.UNKNOWN,
                source=f"derived:{method}",
                kind=EvidenceKind.DERIVED,
                method=method,
                lineage=lineage,
            ),
            unit=unit,
        )

    grade = _minimum_grade(inputs)
    if max_grade is not None and GRADE_RANK[grade] > GRADE_RANK[max_grade]:
        grade = max_grade
    return ObservedValue(
        value,
        Evidence(
            grade=grade,
            source=f"derived:{method}",
            kind=EvidenceKind.DERIVED,
            method=method,
            lineage=lineage,
        ),
        unit=unit,
    )


def _require_observation(name: str, observed: ObservedValue | None, reasons: list[str]) -> None:
    if observed is None or observed.value is None:
        reasons.append(f"{name}_missing")
    elif observed.evidence.grade == EvidenceGrade.UNKNOWN:
        reasons.append(f"{name}_evidence_unknown")


def lease_economics(offer: AcquisitionOffer, profile: UserProfile) -> dict[str, Any]:
    if offer.mode != AcquisitionMode.LEASE_NEW:
        raise PurchaseMethodBlockedError(
            "Purchase economics are blocked until original P1-P3 findings and economics anchors are recovered."
        )

    reasons: list[str] = []
    required = {
        "term_months": offer.term_months,
        "upfront_payment": offer.upfront_payment,
        "recurring_payment": offer.recurring_payment,
        "mandatory_fees": offer.mandatory_fees,
    }
    for name, observed in required.items():
        _require_observation(name, observed, reasons)

    term_months = _value(offer.term_months)
    upfront = _value(offer.upfront_payment)
    recurring = _value(offer.recurring_payment)
    fees = _value(offer.mandatory_fees)
    base_inputs = [v for v in required.values() if v is not None and v.value is not None]

    base_cash_cost = None
    if term_months is not None and upfront is not None and recurring is not None and fees is not None:
        base_cash_cost = upfront + recurring * term_months + fees

    expected_total_km = None
    contracted_total_km = None
    mileage_adjustment = None
    overage_cost = 0.0
    unused_km_value_loss = 0.0
    mileage_inputs: list[ObservedValue] = []
    scenario_adjusted = False

    if profile.expected_annual_km is None:
        reasons.append("expected_annual_km_missing")
    elif offer.annual_km is None or offer.annual_km.value is None:
        reasons.append("annual_km_missing")
    elif term_months is not None:
        if offer.annual_km.evidence.grade == EvidenceGrade.UNKNOWN:
            reasons.append("annual_km_evidence_unknown")
        annual_km = _value(offer.annual_km)
        years = term_months / 12.0
        expected_total_km = profile.expected_annual_km * years
        contracted_total_km = annual_km * years
        delta = expected_total_km - contracted_total_km
        scenario_adjusted = delta != 0
        mileage_inputs = [offer.annual_km, offer.term_months]

        if delta > 0:
            if offer.overage_cost_per_km is None or offer.overage_cost_per_km.value is None:
                overage_cost = None
                mileage_adjustment = None
                reasons.append("overage_cost_per_km_missing")
            else:
                if offer.overage_cost_per_km.evidence.grade == EvidenceGrade.UNKNOWN:
                    reasons.append("overage_cost_per_km_evidence_unknown")
                overage_cost = delta * _value(offer.overage_cost_per_km)
                unused_km_value_loss = 0.0
                mileage_adjustment = overage_cost
                mileage_inputs.append(offer.overage_cost_per_km)
        elif delta < 0:
            if profile.unused_km_value_per_km is None or profile.unused_km_value_per_km.value is None:
                unused_km_value_loss = None
                mileage_adjustment = None
                reasons.append("unused_km_value_per_km_missing")
            else:
                if profile.unused_km_value_per_km.evidence.grade == EvidenceGrade.UNKNOWN:
                    reasons.append("unused_km_value_per_km_evidence_unknown")
                unused_km_value_loss = (-delta) * _value(profile.unused_km_value_per_km)
                overage_cost = 0.0
                mileage_adjustment = unused_km_value_loss
                mileage_inputs.append(profile.unused_km_value_per_km)
        else:
            mileage_adjustment = 0.0

    total_adjusted_cost = None
    if base_cash_cost is not None and mileage_adjustment is not None:
        total_adjusted_cost = base_cash_cost + mileage_adjustment

    total_inputs = base_inputs + mileage_inputs
    derived = {
        "economics.base_cash_cost": _derived_value(
            base_cash_cost,
            inputs=base_inputs,
            unit=offer.currency,
            method="lease_base_cash_cost",
        ),
        "economics.total_adjusted_cost": _derived_value(
            total_adjusted_cost,
            inputs=total_inputs,
            unit=offer.currency,
            method="lease_total_adjusted_cost",
            max_grade=EvidenceGrade.ESTIMATED if scenario_adjusted else None,
            extra_lineage=("user_profile.expected_annual_km",) if scenario_adjusted else (),
        ),
    }

    return {
        "base_cash_cost": base_cash_cost,
        "overage_cost": overage_cost,
        "unused_km_value_loss": unused_km_value_loss,
        "mileage_adjustment": mileage_adjustment,
        "expected_total_km": expected_total_km,
        "contracted_total_km": contracted_total_km,
        "total_adjusted_cost": total_adjusted_cost,
        "complete": not reasons,
        "reasons": tuple(dict.fromkeys(reasons)),
        "derived_attributes": derived,
    }
