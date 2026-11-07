"""Independent falsifiers for the public offer-checker's claims.

Expected amounts are direct decimal/cash-flow oracles, not copied engine output.
These tests do not establish source truth, current availability or AI conformance.
"""
from copy import deepcopy

import pytest

from glassbox_auto.offer_check import (
    OfferCheckError,
    evaluate_request,
    request_fingerprint,
    validate_request,
)


def specimen():
    return {
        "schema_version": "offer-check-request.v1",
        "policy_id": "dk-private-lease.v1",
        "assessment_at": "2026-11-07T10:00:00Z",
        "profile": {
            "expected_annual_km": 15000,
            "max_initial_non_monthly_dkk": 20000,
            "max_monthly_dkk": 5000,
            "monthly_budget_basis": "LEASE_AND_INSURANCE",
        },
        "confirmation": None,
        "offers": [{
            "offer_id": "independent-a",
            "vehicle": "Independent synthetic EV",
            "mode": "LEASE_NEW",
            "currency": "DKK",
            "source": {
                "kind": "SYNTHETIC",
                "locator": "Synthetic arithmetic oracle; not a market offer",
                "url": None,
                "observed_on": "2026-11-07",
                "valid_until": None,
                "conflict": False,
            },
            "term_months": 36,
            "monthly_payment_count": 36,
            "annual_km": 15000,
            "upfront_payment_dkk": 15000,
            "monthly_payment_dkk": 3500,
            "mandatory_fees_dkk": 1200,
            "fees_upfront_dkk": 600,
            "refundable_deposit_dkk": 4000,
            "monthly_insurance_dkk": 500,
            "overage_dkk_per_km": 1.5,
        }],
    }


def confirmed(request):
    request = deepcopy(request)
    request["confirmation"] = {"request_sha256": request_fingerprint(request)}
    return request


def assert_invalid(request, exit_code=2):
    with pytest.raises(OfferCheckError) as error:
        validate_request(request, require_confirmation=False)
    assert error.value.exit_code == exit_code


@pytest.mark.parametrize("field,value", [
    ("term_months", 36.5),
    ("monthly_payment_count", 35),
    ("annual_km", 0),
    ("upfront_payment_dkk", -0.01),
    ("monthly_payment_dkk", True),
    ("monthly_payment_dkk", 3500.001),
    ("monthly_payment_dkk", 1e308),
    ("monthly_payment_dkk", 1e100),
    ("mandatory_fees_dkk", "1200"),
    ("fees_upfront_dkk", 1200.01),
    ("overage_dkk_per_km", 1.0000001),
])
def test_invalid_lease_money_schedule_and_fee_subset(field, value):
    request = specimen()
    request["offers"][0][field] = value
    assert_invalid(request)


@pytest.mark.parametrize("field", ["observed_on", "valid_until"])
def test_invalid_source_calendar_is_not_hidden_by_purchase_dispatch(field):
    request = specimen()
    request["offers"][0]["mode"] = "BUY_USED"
    request["offers"][0]["source"][field] = "2026-02-30"
    assert_invalid(request, 2)


def test_duplicate_id_is_not_hidden_by_purchase_dispatch():
    request = specimen()
    request["offers"][0]["mode"] = "BUY_NEW"
    request["offers"].append(deepcopy(request["offers"][0]))
    assert_invalid(request, 2)


def test_confirmed_request_change_cannot_reuse_confirmation():
    request = confirmed(specimen())
    request["offers"][0]["mandatory_fees_dkk"] = 0
    request["offers"][0]["fees_upfront_dkk"] = 0
    with pytest.raises(OfferCheckError) as error:
        evaluate_request(request)
    assert error.value.exit_code == 2


def test_source_claim_change_cannot_reuse_confirmation():
    request = confirmed(specimen())
    request["offers"][0]["source"]["conflict"] = True
    with pytest.raises(OfferCheckError) as error:
        evaluate_request(request)
    assert error.value.exit_code == 2


def test_stale_confirmation_is_not_hidden_by_purchase_dispatch():
    request = confirmed(specimen())
    request["offers"][0]["mode"] = "BUY_USED"
    with pytest.raises(OfferCheckError) as error:
        evaluate_request(request)
    assert error.value.exit_code == 2


def test_asserted_verified_evidence_is_rejected():
    request = specimen()
    request["offers"][0]["source"]["grade"] = "VERIFIED"
    assert_invalid(request)


def test_future_observation_is_invalid():
    request = specimen()
    request["offers"][0]["source"]["observed_on"] = "2026-11-08"
    assert_invalid(request)


def test_currency_is_not_silently_converted():
    request = specimen()
    request["offers"][0]["currency"] = "EUR"
    assert_invalid(request, 6)


def test_empty_bundle_has_distinct_exit():
    request = specimen()
    request["offers"] = []
    assert_invalid(request, 5)


def test_mode_and_schedule_contract_has_no_silent_lease_coercion():
    request = specimen()
    request["offers"][0]["mode"] = "BUY_USED"
    for key in list(request["offers"][0]):
        if key not in {"offer_id", "vehicle", "mode", "currency", "source"}:
            del request["offers"][0][key]
    assert_invalid(request, 3)


def test_normalization_does_not_mutate_callers_request():
    request = specimen()
    second = deepcopy(request["offers"][0])
    second["offer_id"] = "another-offer"
    request["offers"].append(second)
    original = deepcopy(request)
    normalized = validate_request(request, require_confirmation=False)
    assert request == original
    assert [offer["offer_id"] for offer in normalized["offers"]] == [
        "another-offer", "independent-a"
    ]


def test_offer_order_changes_do_not_change_request_fingerprint():
    request = specimen()
    second = deepcopy(request["offers"][0])
    second["offer_id"] = "another-offer"
    request["offers"].append(second)
    reversed_request = deepcopy(request)
    reversed_request["offers"].reverse()
    assert request_fingerprint(request) == request_fingerprint(reversed_request)


def single_result(request):
    return evaluate_request(confirmed(request))["offers"][0]


def test_compulsory_fees_count_once_deposit_is_cash_not_cost():
    result = single_result(specimen())
    # 15,000 + (36 * 3,500) + 1,200; refundable 4,000 is not cost.
    assert result["economics"]["base_contract_cost_dkk"] == 142200
    assert result["economics"]["average_contract_cost_per_month_dkk"] == 3950
    # The 600 initial fees are part of 1,200 total, not another 600 cost.
    assert result["budget"]["initial_non_monthly"]["amount_dkk"] == 19600
    assert result["budget"]["recurring_monthly"]["amount_dkk"] == 4000


@pytest.mark.parametrize("field", ["mandatory_fees_dkk", "monthly_payment_count"])
def test_unknown_schedule_or_compulsory_cost_cannot_be_zero_filled(field):
    request = specimen()
    request["offers"][0][field] = None
    result = single_result(request)
    assert result["economics"]["base_contract_cost_dkk"] is None
    assert result["calculation_status"] == "INCOMPLETE_INPUTS"


@pytest.mark.parametrize("field", ["fees_upfront_dkk", "refundable_deposit_dkk"])
def test_unknown_initial_cash_cannot_pass_budget(field):
    request = specimen()
    request["offers"][0][field] = None
    result = single_result(request)
    assert result["budget"]["initial_non_monthly"]["amount_dkk"] is None
    assert result["budget"]["initial_non_monthly"]["status"] == "UNKNOWN"
    assert result["economics"]["base_contract_cost_dkk"] == 142200


def test_missing_insurance_prevents_lease_plus_insurance_budget_pass():
    request = specimen()
    request["offers"][0]["monthly_insurance_dkk"] = None
    result = single_result(request)
    assert result["budget"]["recurring_monthly"]["amount_dkk"] is None
    assert result["budget"]["recurring_monthly"]["status"] == "UNKNOWN"
    request["profile"]["monthly_budget_basis"] = "LEASE_ONLY"
    result = single_result(request)
    assert result["budget"]["recurring_monthly"]["amount_dkk"] == 3500
    assert result["budget"]["recurring_monthly"]["status"] == "WITHIN_ENTERED_LIMIT"


def test_overage_is_separate_scenario_and_missing_rate_keeps_unknown():
    request = specimen()
    request["profile"]["expected_annual_km"] = 20000
    result = single_result(request)
    assert result["economics"]["expected_total_km"] == 60000
    assert result["economics"]["contracted_total_km"] == 45000
    assert result["economics"]["overage_cost_dkk"] == 22500
    assert result["economics"]["expected_mileage_cost_dkk"] == 164700
    assert result["economics"]["base_contract_cost_dkk"] == 142200
    assert result["recommendation"] == "NOT_ASSESSED"
    request["offers"][0]["overage_dkk_per_km"] = None
    result = single_result(request)
    assert result["economics"]["overage_cost_dkk"] is None
    assert result["economics"]["expected_mileage_cost_dkk"] is None
    assert result["economics"]["base_contract_cost_dkk"] == 142200


@pytest.mark.parametrize("missing", ["annual_km", "expected_annual_km"])
def test_missing_mileage_never_means_zero_overage(missing):
    request = specimen()
    if missing == "expected_annual_km":
        request["profile"][missing] = None
    else:
        request["offers"][0][missing] = None
    result = single_result(request)
    assert result["economics"]["base_contract_cost_dkk"] == 142200
    assert result["economics"]["expected_mileage_cost_dkk"] is None
    assert result["economics"]["overage_cost_dkk"] is None


def test_underuse_does_not_invent_refund_or_loss():
    request = specimen()
    request["profile"]["expected_annual_km"] = 10000
    result = single_result(request)
    assert result["economics"]["expected_mileage_cost_dkk"] == 142200
    assert result["economics"]["overage_cost_dkk"] == 0
    assert result["warnings"]


def test_budget_cents_are_exact_at_large_domain_boundary():
    request = specimen()
    request["profile"]["max_initial_non_monthly_dkk"] = 10_000_000
    request["offers"][0].update({
        "upfront_payment_dkk": 2656572.97,
        "mandatory_fees_dkk": 6260967.48,
        "fees_upfront_dkk": 6260967.48,
        "refundable_deposit_dkk": 1082459.55,
    })
    # Naive binary64 sum is 10000000.000000002, exceeding a 1e-9 tolerance.
    result = single_result(request)
    budget = result["budget"]["initial_non_monthly"]
    assert budget["amount_dkk"] == 10_000_000
    assert budget["status"] == "WITHIN_ENTERED_LIMIT"
    request["offers"][0]["refundable_deposit_dkk"] = 1082459.56
    result = single_result(request)
    assert result["budget"]["initial_non_monthly"]["status"] == "EXCEEDS_ENTERED_LIMIT"


def test_small_cent_boundary_does_not_false_fail():
    request = specimen()
    request["offers"][0]["monthly_payment_dkk"] = 0.1
    request["offers"][0]["monthly_insurance_dkk"] = 0.2
    request["profile"]["max_monthly_dkk"] = 0.3
    result = single_result(request)
    assert result["budget"]["recurring_monthly"]["amount_dkk"] == 0.3
    assert result["budget"]["recurring_monthly"]["status"] == "WITHIN_ENTERED_LIMIT"


def test_traceable_assertions_never_become_verified_or_recommendation():
    request = specimen()
    request["offers"][0]["source"].update({
        "kind": "USER_SUPPLIED", "locator": "Synthetic written quote 123",
        "url": "https://example.com/dated-offer", "observed_on": "2026-11-07",
        "valid_until": "2026-11-30", "conflict": False,
    })
    result = single_result(request)
    assert result["source_verification"] == "UNVERIFIED"
    assert result["recommendation"] == "NOT_ASSESSED"
    assert result["warnings"]


def test_expiry_and_conflict_remain_visible_with_complete_arithmetic():
    request = specimen()
    request["offers"][0]["source"].update({
        "kind": "USER_SUPPLIED", "valid_until": "2026-11-06", "conflict": True,
        "observed_on": "2026-11-01",
    })
    result = single_result(request)
    assert result["economics"]["base_contract_cost_dkk"] == 142200
    assert result["source"]["expired"] is True
    assert result["source"]["age_days"] == 6
    assert "OFFER_EXPIRED" in result["warnings"]
    assert "SOURCE_CONFLICT_UNRESOLVED" in result["warnings"]
    assert result["source_verification"] == "UNVERIFIED"
    assert result["recommendation"] == "NOT_ASSESSED"


def test_date_only_expiry_is_not_shortened_to_start_of_day():
    request = specimen()
    request["assessment_at"] = "2026-11-07T23:59:59Z"
    request["offers"][0]["source"]["valid_until"] = "2026-11-07"
    result = single_result(request)
    assert result["source"]["expired"] is False
    assert "OFFER_EXPIRED" not in result["warnings"]
    assert result["source_verification"] == "UNVERIFIED"


@pytest.mark.parametrize("term,upfront,monthly,fees,expected_total", [
    (48, 15000, 4595, 6095, 241655),
    (36, 19995, 5045, 1000, 202615),
    (48, 5000, 4995, 600, 245360),
])
def test_fixed_historical_fdm_published_totals(term, upfront, monthly, fees, expected_total):
    """Reconcile FDM's dated 2024 examples, never present them as live offers.

    Source: FDM, '5 farlige leasingfælder', 17 October 2024, table with prices
    gathered 14 October 2024. Mileage supplements are included in monthly.
    The published totals are an external arithmetic oracle, not a price feed.
    """
    request = specimen()
    offer = request["offers"][0]
    offer.update({
        "vehicle": "Historical published arithmetic example; not a live offer",
        "term_months": term, "monthly_payment_count": term,
        "upfront_payment_dkk": upfront, "monthly_payment_dkk": monthly,
        "mandatory_fees_dkk": fees, "fees_upfront_dkk": None,
        "refundable_deposit_dkk": None, "monthly_insurance_dkk": None,
        "overage_dkk_per_km": None,
    })
    offer["source"].update({
        "kind": "USER_SUPPLIED",
        "locator": "FDM historical comparison, published 17 October 2024; prices 14 October 2024",
        "url": "https://fdm.dk/nyheder/nyt-om-trafik-og-biler/2024-10-5-farlige-leasingfaelder-der-kan-koste-dig-kassen",
        "observed_on": "2024-10-14",
    })
    result = single_result(request)
    assert result["economics"]["base_contract_cost_dkk"] == expected_total
    assert result["source_verification"] == "UNVERIFIED"
    assert result["recommendation"] == "NOT_ASSESSED"
