import pytest

from glassbox_auto.compat.v3_economics import (
    RecoveredV3HouseholdProfile,
    RecoveredV3LeaseOffer,
    calculated_contract_total,
    comparison_total,
    effective_monthly,
    energy_monthly,
    first_12_month_burden,
    household_monthly,
    insurance_monthly,
    stress_household_monthly,
)


def recovered_profile():
    return RecoveredV3HouseholdProfile(
        expected_annual_km=9000,
        stress_annual_km=15000,
        default_insurance_annual=6500,
        default_kwh_per_100km=19,
        home_charging_share=0.8,
        home_electricity_price=1.4,
        public_electricity_price=3.5,
        parking_annual=1200,
        vehicle_tax_annual=840,
        wear_reserve_total=4000,
    )


def bmw_ix3_40_offer():
    # Recovered workbook Offers_Data row for BMW-IX3-40.
    return RecoveredV3LeaseOffer(
        contracted_annual_km=15000,
        term_months=48,
        first_payment=35000,
        monthly_payment=5495,
        establishment_fee=4995,
        admin_monthly=25,
        return_fee=0,
        stated_total=304955,
        overage_per_km=2,
        insurance_quote_annual=None,
        measured_kwh_per_100km=None,
    )


def test_bmw_ix3_40_reproduces_recovered_workbook_economics_cells():
    profile = recovered_profile()
    offer = bmw_ix3_40_offer()

    assert calculated_contract_total(offer) == pytest.approx(304955.0)
    assert comparison_total(offer) == pytest.approx(304955.0)
    assert effective_monthly(offer) == pytest.approx(6353.22916666667)
    assert energy_monthly(profile, offer, annual_km=9000) == pytest.approx(259.35)
    assert insurance_monthly(profile, offer) == pytest.approx(541.666666666667)
    assert household_monthly(profile, offer) == pytest.approx(7407.57916666667)
    assert first_12_month_burden(profile, offer) == pytest.approx(117887.2)
    assert stress_household_monthly(profile, offer) == pytest.approx(7580.47916666667)


def test_stated_total_never_understates_calculated_contract_total():
    offer = RecoveredV3LeaseOffer(
        contracted_annual_km=15000,
        term_months=36,
        first_payment=10000,
        monthly_payment=4000,
        establishment_fee=1000,
        admin_monthly=0,
        return_fee=500,
        stated_total=100000,
        overage_per_km=2,
    )
    assert calculated_contract_total(offer) == 155500
    assert comparison_total(offer) == 155500


def test_measured_consumption_and_insurance_quote_supersede_defaults():
    profile = recovered_profile()
    offer = RecoveredV3LeaseOffer(
        contracted_annual_km=15000,
        term_months=36,
        first_payment=10000,
        monthly_payment=4000,
        establishment_fee=1000,
        admin_monthly=0,
        return_fee=0,
        stated_total=None,
        overage_per_km=2,
        insurance_quote_annual=7200,
        measured_kwh_per_100km=16,
    )
    assert insurance_monthly(profile, offer) == 600
    assert energy_monthly(profile, offer, annual_km=9000) == pytest.approx(218.4)


def test_underuse_is_not_monetized_in_recovered_household_economics():
    profile = recovered_profile()
    offer = bmw_ix3_40_offer()
    # 9,000 expected vs 15,000 contracted: the recovered formula has only
    # MAX(0, expected-contracted) over-km cost and no unused-km deduction.
    assert household_monthly(profile, offer) == pytest.approx(7407.57916666667)
