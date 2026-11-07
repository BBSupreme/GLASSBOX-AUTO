"""Offer-checker product contracts, independent of legacy ranking policies."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from glassbox_auto.offer_check import (
    OfferCheckError, evaluate_request, request_fingerprint,
    validate_decision, validate_request,
)
from glassbox_auto.wire import sha256


EXAMPLES = Path(__file__).parents[1] / "src/glassbox_auto/examples"


def draft(name="complete"):
    return json.loads((EXAMPLES / f"{name}.json").read_text())


def sign(value):
    value = deepcopy(value)
    value["confirmation"] = None
    value["confirmation"] = {"request_sha256": request_fingerprint(validate_request(value, False))}
    return value


def one(value):
    return evaluate_request(sign(value))["offers"][0]


def test_complete_preserves_cost_views_and_evidence_boundary():
    result = one(draft())
    assert result["economics"]["base_contract_cost_dkk"] == 141600
    assert result["economics"]["expected_mileage_cost_dkk"] == 141600
    assert result["economics"]["average_contract_cost_per_month_dkk"] == pytest.approx(3933.333333333333)
    assert result["budget"]["initial_non_monthly"]["amount_dkk"] == 15000
    assert result["budget"]["recurring_monthly"]["amount_dkk"] == 4000
    assert result["source_verification"] == "UNVERIFIED"
    assert result["recommendation"] == "NOT_ASSESSED"
    assert result["source"]["expired"] is None
    assert result["calculation_status"] == "CALCULATED_FROM_INPUTS"


def test_missing_fees_and_insurance_are_not_zero():
    result = one(draft("incomplete"))
    assert result["economics"]["base_contract_cost_dkk"] is None
    assert result["economics"]["expected_mileage_cost_dkk"] is None
    assert result["budget"]["initial_non_monthly"]["status"] == "UNKNOWN"
    assert result["budget"]["recurring_monthly"]["status"] == "UNKNOWN"
    assert result["calculation_status"] == "INCOMPLETE_INPUTS"
    assert "mandatory_fees_dkk" in result["missing_fields"]


def test_expired_conflict_and_mileage_are_scenario_only():
    result = one(draft("over-mileage"))
    assert result["economics"]["overage_cost_dkk"] == 45000
    assert result["economics"]["expected_mileage_cost_dkk"] == 186600
    assert result["source"]["age_days"] == 37
    assert result["source"]["expired"] is True
    assert {"OFFER_EXPIRED", "SOURCE_CONFLICT_UNRESOLVED", "EXCESS_MILEAGE_REQUIRES_CONTRACT_CONFIRMATION"} <= set(result["warnings"])
    assert result["recommendation"] == "NOT_ASSESSED"


def test_confirmation_binds_offer_changes_and_source_dates():
    value = sign(draft())
    for section, key, replacement in [
        ("profile", "expected_annual_km", 20000),
        ("offer", "monthly_payment_dkk", 3501),
        ("source", "observed_on", "2026-11-06"),
    ]:
        altered = deepcopy(value)
        target = altered["profile"] if section == "profile" else altered["offers"][0]
        if section == "source":
            target = target["source"]
        target[key] = replacement
        with pytest.raises(OfferCheckError) as error:
            evaluate_request(altered)
        assert error.value.code == "CONFIRMATION_MISMATCH"


def test_offer_order_does_not_change_decision():
    value = draft()
    other = deepcopy(value["offers"][0])
    other["offer_id"] = "second"
    value["offers"].append(other)
    forward = evaluate_request(sign(value))
    value["offers"].reverse()
    reverse = evaluate_request(sign(value))
    assert forward == reverse
    assert sha256(forward) == sha256(reverse)


def test_confirmation_is_required_before_purchase_mode_dispatch():
    value = draft()
    value["offers"][0] = {key: value["offers"][0][key] for key in ["offer_id", "vehicle", "mode", "currency", "source"]}
    value["offers"][0]["mode"] = "BUY_USED"
    with pytest.raises(OfferCheckError) as error:
        validate_request(value)
    assert error.value.code == "CONFIRMATION_REQUIRED"
    # Explicit method diagnosis does not require fabricated lease fields.
    value["confirmation"] = {"request_sha256": request_fingerprint(value)}
    with pytest.raises(OfferCheckError) as error:
        validate_request(value)
    assert error.value.exit_code == 3


def test_unknown_payment_count_does_not_guess_full_term():
    value = draft()
    value["offers"][0]["monthly_payment_count"] = None
    result = one(value)
    assert result["economics"]["base_contract_cost_dkk"] is None
    assert "monthly_payment_count" in result["missing_fields"]


def test_result_validation_rejects_wrong_identity_and_extra_claims():
    value = sign(draft())
    result = evaluate_request(value)
    assert validate_decision(result, value) == result
    result["profile_sha256"] = "0" * 64
    with pytest.raises(OfferCheckError) as error:
        validate_decision(result, value)
    assert error.value.exit_code == 4
    result = evaluate_request(value)
    result["offers"][0]["verified"] = True
    with pytest.raises(OfferCheckError):
        validate_decision(result, value)


@pytest.mark.parametrize("amount", [0.07, 0.29, 1.14, 9999999.99])
def test_valid_cent_amounts_survive_structural_schema(amount):
    value = draft()
    value["offers"][0]["monthly_payment_dkk"] = amount
    assert validate_request(value, False)["offers"][0]["monthly_payment_dkk"] == amount


@pytest.mark.parametrize("amount", [True, -1, 0.001, 10000000.01, 1e100, 1e308])
def test_invalid_money_is_safe_validation_error(amount):
    value = draft()
    value["offers"][0]["monthly_payment_dkk"] = amount
    with pytest.raises(OfferCheckError) as error:
        validate_request(value, False)
    assert error.value.exit_code == 2
    assert str(amount) not in str(error.value)
