from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class RecoveredV3HouseholdProfile:
    expected_annual_km: float
    stress_annual_km: float
    default_insurance_annual: float
    default_kwh_per_100km: float
    home_charging_share: float
    home_electricity_price: float
    public_electricity_price: float
    parking_annual: float
    vehicle_tax_annual: float
    wear_reserve_total: float

    def __post_init__(self) -> None:
        values = (
            self.expected_annual_km,
            self.stress_annual_km,
            self.default_insurance_annual,
            self.default_kwh_per_100km,
            self.home_charging_share,
            self.home_electricity_price,
            self.public_electricity_price,
            self.parking_annual,
            self.vehicle_tax_annual,
            self.wear_reserve_total,
        )
        if not all(_finite(value) for value in values):
            raise ValueError("Recovered v3 household inputs must be finite")
        if self.expected_annual_km < 0 or self.stress_annual_km < 0:
            raise ValueError("Annual km must be non-negative")
        if not 0 <= self.home_charging_share <= 1:
            raise ValueError("home_charging_share must be within [0, 1]")
        if any(value < 0 for value in values[2:]):
            raise ValueError("Recovered v3 household cost inputs must be non-negative")


@dataclass(frozen=True)
class RecoveredV3LeaseOffer:
    contracted_annual_km: float
    term_months: float
    first_payment: float
    monthly_payment: float
    establishment_fee: float
    admin_monthly: float
    return_fee: float
    stated_total: float | None
    overage_per_km: float
    insurance_quote_annual: float | None = None
    measured_kwh_per_100km: float | None = None

    def __post_init__(self) -> None:
        required = (
            self.contracted_annual_km,
            self.term_months,
            self.first_payment,
            self.monthly_payment,
            self.establishment_fee,
            self.admin_monthly,
            self.return_fee,
            self.overage_per_km,
        )
        if not all(_finite(value) for value in required):
            raise ValueError("Recovered v3 lease inputs must be finite")
        if self.contracted_annual_km <= 0 or self.term_months <= 0:
            raise ValueError("Contracted annual km and term must be positive")
        if any(value < 0 for value in required[2:]):
            raise ValueError("Recovered v3 lease cost inputs must be non-negative")
        for optional in (self.stated_total, self.insurance_quote_annual, self.measured_kwh_per_100km):
            if optional is not None and (not _finite(optional) or optional < 0):
                raise ValueError("Optional recovered v3 lease inputs must be finite and non-negative")


def _finite(value: float) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def calculated_contract_total(offer: RecoveredV3LeaseOffer) -> float:
    return (
        offer.first_payment
        + offer.monthly_payment * offer.term_months
        + offer.establishment_fee
        + offer.admin_monthly * offer.term_months
        + offer.return_fee
    )


def comparison_total(offer: RecoveredV3LeaseOffer) -> float:
    calculated = calculated_contract_total(offer)
    if offer.stated_total is None:
        return calculated
    return max(offer.stated_total, calculated)


def effective_monthly(offer: RecoveredV3LeaseOffer) -> float:
    return comparison_total(offer) / offer.term_months


def blended_electricity_price(profile: RecoveredV3HouseholdProfile) -> float:
    return (
        profile.home_charging_share * profile.home_electricity_price
        + (1 - profile.home_charging_share) * profile.public_electricity_price
    )


def energy_monthly(
    profile: RecoveredV3HouseholdProfile,
    offer: RecoveredV3LeaseOffer,
    *,
    annual_km: float,
) -> float:
    consumption = (
        offer.measured_kwh_per_100km
        if offer.measured_kwh_per_100km is not None and offer.measured_kwh_per_100km > 0
        else profile.default_kwh_per_100km
    )
    return annual_km / 12 * consumption / 100 * blended_electricity_price(profile)


def insurance_monthly(profile: RecoveredV3HouseholdProfile, offer: RecoveredV3LeaseOffer) -> float:
    annual = (
        offer.insurance_quote_annual
        if offer.insurance_quote_annual is not None and offer.insurance_quote_annual > 0
        else profile.default_insurance_annual
    )
    return annual / 12


def overage_monthly(offer: RecoveredV3LeaseOffer, *, annual_km: float) -> float:
    return max(0.0, annual_km - offer.contracted_annual_km) / 12 * offer.overage_per_km


def household_monthly(profile: RecoveredV3HouseholdProfile, offer: RecoveredV3LeaseOffer) -> float:
    return (
        effective_monthly(offer)
        + energy_monthly(profile, offer, annual_km=profile.expected_annual_km)
        + insurance_monthly(profile, offer)
        + (profile.parking_annual + profile.vehicle_tax_annual) / 12
        + profile.wear_reserve_total / offer.term_months
        + overage_monthly(offer, annual_km=profile.expected_annual_km)
    )


def first_12_month_burden(profile: RecoveredV3HouseholdProfile, offer: RecoveredV3LeaseOffer) -> float:
    monthly_operating_without_wear = (
        energy_monthly(profile, offer, annual_km=profile.expected_annual_km)
        + insurance_monthly(profile, offer)
        + (profile.parking_annual + profile.vehicle_tax_annual) / 12
    )
    return (
        offer.first_payment
        + offer.monthly_payment * 12
        + offer.establishment_fee
        + offer.admin_monthly * 12
        + monthly_operating_without_wear * 12
    )


def stress_household_monthly(profile: RecoveredV3HouseholdProfile, offer: RecoveredV3LeaseOffer) -> float:
    normal = household_monthly(profile, offer)
    normal_energy = energy_monthly(profile, offer, annual_km=profile.expected_annual_km)
    normal_overage = overage_monthly(offer, annual_km=profile.expected_annual_km)
    stress_energy = energy_monthly(profile, offer, annual_km=profile.stress_annual_km)
    stress_overage = overage_monthly(offer, annual_km=profile.stress_annual_km)
    return normal - normal_energy - normal_overage + stress_energy + stress_overage


def relative_economics_score(household_monthly_cost: float, minimum_household_monthly_cost: float) -> float:
    if not _finite(household_monthly_cost) or not _finite(minimum_household_monthly_cost):
        raise ValueError("Economics score inputs must be finite")
    if household_monthly_cost <= 0 or minimum_household_monthly_cost <= 0:
        raise ValueError("Economics score inputs must be positive")
    return 10 * minimum_household_monthly_cost / household_monthly_cost
