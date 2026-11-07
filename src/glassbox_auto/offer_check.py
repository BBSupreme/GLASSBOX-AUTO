"""Deterministic arithmetic for explicitly entered Danish private-lease offers.

This adapter never authenticates sources, ranks cars, or marks a purchase ready.
The canonical engine owns lease economics; this module owns strict input and the
small, explicit cash-budget view documented in OFFER_CHECK_CONTRACT_v1.md.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlsplit

from . import __version__
from .economics import lease_economics
from .integrity import require_finite_tree, require_identifier
from .models import AcquisitionMode, AcquisitionOffer, Evidence, EvidenceGrade, ObservedValue, UserProfile
from .offer_policy import (
    CANONICALIZATION_ID, LEASE_FIELDS, LIMITATIONS, POLICY_ID,
    RESULT_SCHEMA_VERSION, SCHEMA_VERSION,
)
from .wire import WireError, canonical_bytes, normalize_json, sha256


class OfferCheckError(ValueError):
    """Safe diagnostic: field paths and fixed codes, never input values."""

    def __init__(self, code: str, paths=(), exit_code: int = 2):
        self.code = code
        self.paths = tuple(sorted(set(paths)))
        self.exit_code = exit_code
        super().__init__(code)


def _fail(code: str, path: str, exit_code: int = 2) -> None:
    raise OfferCheckError(code, (path,), exit_code)


def _matches_type(value: Any, typ: str) -> bool:
    return {
        "null": lambda: value is None,
        "boolean": lambda: isinstance(value, bool),
        "integer": lambda: isinstance(value, int) and not isinstance(value, bool),
        "number": lambda: isinstance(value, (int, float)) and not isinstance(value, bool),
        "string": lambda: isinstance(value, str),
        "array": lambda: isinstance(value, list),
        "object": lambda: isinstance(value, dict),
    }[typ]()


def _validate_schema(value: Any, schema: dict, path: str, errors: list[str]) -> None:
    """Evaluate the package-owned schema subset; never resolve input schemas.

    The public schema is the single structural declaration. Supported keywords
    are deliberately restricted to those present in that immutable local file.
    Semantic date, ID, schedule and consent checks remain below.
    """
    if "anyOf" in schema:
        if not any(_schema_valid(value, branch, path) for branch in schema["anyOf"]):
            errors.append(path)
        return
    if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
        errors.append(path)
        return
    if "enum" in schema and value not in schema["enum"]:
        errors.append(path)
        return
    types = schema.get("type")
    if types is not None:
        types = [types] if isinstance(types, str) else types
        if not any(_matches_type(value, typ) for typ in types):
            errors.append(path)
            return
    if value is None:
        return
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for key in sorted(schema.get("required", [])):
            if key not in value:
                errors.append(f"{path}.{key}")
        if schema.get("additionalProperties") is False and set(value) - set(properties):
            # Do not echo arbitrary attacker-supplied field names in diagnostics.
            errors.append(path)
        for key in sorted(set(value) & set(properties)):
            _validate_schema(value[key], properties[key], f"{path}.{key}", errors)
    elif isinstance(value, list):
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", len(value)):
            errors.append(path)
        for index, item in enumerate(value):
            _validate_schema(item, schema["items"], f"{path}[{index}]", errors)
    elif isinstance(value, str):
        if not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", len(value)):
            errors.append(path)
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            errors.append(path)
        if schema.get("format") == "date":
            try:
                if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
                    raise ValueError
                date.fromisoformat(value)
            except ValueError:
                errors.append(path)
        elif schema.get("format") == "date-time":
            try:
                if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value) is None:
                    raise ValueError
                datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                errors.append(path)
        elif schema.get("format") == "uri":
            try:
                parsed = urlsplit(value)
                if (
                    parsed.scheme not in {"http", "https"} or not parsed.hostname
                    or parsed.username is not None or parsed.password is not None
                    or any(character.isspace() or ord(character) < 32 for character in value)
                ):
                    raise ValueError
                parsed.port  # also reject invalid port syntax/range
            except ValueError:
                errors.append(path)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema.get("minimum", value) or value > schema.get("maximum", value):
            errors.append(path)
            return
        if "x-decimal-places" in schema and Decimal(str(value)) % Decimal(10) ** -schema["x-decimal-places"] != 0:
            errors.append(path)


def _schema_valid(value: Any, schema: dict, path: str) -> bool:
    errors: list[str] = []
    _validate_schema(value, schema, path, errors)
    return not errors


def request_fingerprint(request: dict) -> str:
    """Hash normalized material inputs, excluding the confirmation envelope.

    This helper does not validate or authenticate assent. Call validate_request
    with require_confirmation=False first when preparing untrusted inputs.
    """
    value = deepcopy(request)
    value.pop("confirmation", None)
    if isinstance(value.get("offers"), list):
        value["offers"] = sorted(value["offers"], key=lambda item: item["offer_id"])
    return sha256(value)


def profile_fingerprint(profile: dict, policy_id: str = POLICY_ID) -> str:
    return sha256({"policy_id": policy_id, "profile": profile})


def validate_request(request: dict, require_confirmation: bool = True) -> dict:
    """Return a normalized independent copy or a safe phase-ordered error."""
    try:
        normalized = normalize_json(request)
    except WireError as exc:
        raise OfferCheckError(exc.code, exc.paths, exc.exit_code) from None
    schema_path = Path(__file__).with_name("schemas") / "offer-check-request.v1.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    _validate_schema(normalized, schema, "$", errors)
    if errors:
        raise OfferCheckError("INVALID_REQUEST", errors)

    assessment_day = datetime.strptime(normalized["assessment_at"], "%Y-%m-%dT%H:%M:%SZ").date()
    seen: set[str] = set()
    for index, offer in enumerate(normalized["offers"]):
        path = f"$.offers[{index}]"
        for key in ("offer_id", "vehicle"):
            try:
                require_identifier(offer[key], key)
                if len(offer[key].encode("utf-8")) > 256:
                    raise ValueError
            except ValueError:
                errors.append(f"{path}.{key}")
        if offer["offer_id"] in seen:
            errors.append(f"{path}.offer_id")
        seen.add(offer["offer_id"])
        observed = offer["source"]["observed_on"]
        if observed is not None and date.fromisoformat(observed) > assessment_day:
            errors.append(f"{path}.source.observed_on")
    if errors:
        raise OfferCheckError("INVALID_REQUEST", errors)

    normalized["offers"].sort(key=lambda offer: offer["offer_id"])
    confirmation = normalized.get("confirmation")
    if require_confirmation:
        if confirmation is None:
            _fail("CONFIRMATION_REQUIRED", "$.confirmation")
        if confirmation["request_sha256"] != request_fingerprint(normalized):
            _fail("CONFIRMATION_MISMATCH", "$.confirmation.request_sha256")
    elif confirmation is not None and confirmation["request_sha256"] != request_fingerprint(normalized):
        _fail("CONFIRMATION_MISMATCH", "$.confirmation.request_sha256")
    # Normalize omitted draft confirmation and explicit null identically.
    normalized["confirmation"] = confirmation

    # General semantics, including supplied confirmation, precede mode dispatch.
    if any(offer["mode"] != "LEASE_NEW" for offer in normalized["offers"]):
        _fail("PURCHASE_METHOD_BLOCKED", "$.offers", 3)

    for index, offer in enumerate(normalized["offers"]):
        path = f"$.offers[{index}]"
        errors.extend(f"{path}.{key}" for key in LEASE_FIELDS if key not in offer)
        if any(key not in offer for key in LEASE_FIELDS):
            continue
        term = offer["term_months"]
        count = offer["monthly_payment_count"]
        if term is not None and count is not None and term != count:
            errors.append(f"{path}.monthly_payment_count")
        fees = offer["mandatory_fees_dkk"]
        initial_fees = offer["fees_upfront_dkk"]
        if fees is not None and initial_fees is not None and initial_fees > fees:
            errors.append(f"{path}.fees_upfront_dkk")
    if errors:
        raise OfferCheckError("INVALID_LEASE_INPUT", errors)
    if any(offer["currency"] != "DKK" for offer in normalized["offers"]):
        _fail("UNSUPPORTED_CURRENCY", "$.offers", 6)
    if not normalized["offers"]:
        _fail("NO_OFFERS", "$.offers", 5)
    return normalized


def code_fingerprint() -> str:
    """Fingerprint installed implementation/schema bytes; works from a wheel.

    It is provenance, not signature/authentication. Examples/results are excluded
    so copying a sample cannot change the execution identity.
    """
    root = Path(__file__).parent
    files = list(root.rglob("*.py")) + list((root / "schemas").glob("*.json"))
    hashes = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(files)
    }
    return sha256(hashes)


def _obs(value: int | float | None, unit: str, source: dict) -> ObservedValue:
    return ObservedValue(
        value,
        Evidence(
            grade=EvidenceGrade.UNKNOWN if value is None else EvidenceGrade.ESTIMATED,
            source=source["url"] or source["locator"] or "user-supplied:unverified",
            as_of=source["observed_on"],
        ),
        unit,
    )


def _cents(value: int | float) -> int:
    return int(Decimal(str(value)) * 100)


def _money_sum(*values: int | float | None) -> float | None:
    if any(value is None for value in values):
        return None
    return sum(_cents(value) for value in values) / 100


def _budget(amount: float | None, limit: int | float | None) -> dict:
    if limit is None:
        status = "NOT_REQUESTED"
    elif amount is None:
        status = "UNKNOWN"
    else:
        status = "WITHIN_ENTERED_LIMIT" if _cents(amount) <= _cents(limit) else "EXCEEDS_ENTERED_LIMIT"
    return {"amount_dkk": amount, "limit_dkk": limit, "status": status}


def _evaluate_offer(offer: dict, profile: dict, assessment_day: date) -> dict:
    source = offer["source"]
    # Unknown number of payments prevents totals; never guess one payment/month.
    schedule_known = offer["term_months"] is not None and offer["monthly_payment_count"] is not None
    engine_offer = AcquisitionOffer(
        offer_id=offer["offer_id"], vehicle_id=offer["offer_id"], mode=AcquisitionMode.LEASE_NEW,
        term_months=_obs(offer["term_months"] if schedule_known else None, "month", source),
        annual_km=_obs(offer["annual_km"], "km/year", source),
        upfront_payment=_obs(offer["upfront_payment_dkk"], "DKK", source),
        recurring_payment=_obs(offer["monthly_payment_dkk"], "DKK/month", source),
        mandatory_fees=_obs(offer["mandatory_fees_dkk"], "DKK", source),
        overage_cost_per_km=_obs(offer["overage_dkk_per_km"], "DKK/km", source),
    )
    engine_profile = UserProfile(
        profile_id="offer-check", criteria=(), expected_annual_km=profile["expected_annual_km"],
        require_unused_km_value=False,
    )
    econ = lease_economics(engine_offer, engine_profile)
    base = econ["base_cash_cost"]
    warnings: list[str] = ["SOURCE_VALUES_UNVERIFIED", "CONFIRM_CURRENT_TERMS"]
    if source["kind"] == "SYNTHETIC":
        warnings.append("SYNTHETIC_NOT_A_MARKET_OFFER")
    if source["url"] is None and source["locator"] is None:
        warnings.append("SOURCE_REFERENCE_MISSING")
    age_days = None
    if source["observed_on"] is None:
        warnings.append("SOURCE_DATE_MISSING")
    else:
        age_days = (assessment_day - date.fromisoformat(source["observed_on"])).days
    expired = None if source["valid_until"] is None else date.fromisoformat(source["valid_until"]) < assessment_day
    if expired:
        warnings.append("OFFER_EXPIRED")
    if source["valid_until"] is None:
        warnings.append("EXPIRY_UNKNOWN")
    if source["conflict"]:
        warnings.append("SOURCE_CONFLICT_UNRESOLVED")

    expected = profile["expected_annual_km"]
    contracted = offer["annual_km"]
    if expected is not None and contracted is not None:
        if expected > contracted:
            warnings.append("EXCESS_MILEAGE_REQUIRES_CONTRACT_CONFIRMATION")
        elif expected < contracted:
            warnings.append("UNDER_MILEAGE_REFUND_NOT_ASSUMED")

    missing = [key for key in ("term_months", "monthly_payment_count", "upfront_payment_dkk", "monthly_payment_dkk", "mandatory_fees_dkk") if offer[key] is None]
    if expected is None:
        missing.append("profile.expected_annual_km")
    if contracted is None:
        missing.append("annual_km")
    if expected is not None and contracted is not None and expected > contracted and offer["overage_dkk_per_km"] is None:
        missing.append("overage_dkk_per_km")
    if profile["max_initial_non_monthly_dkk"] is not None:
        missing.extend(key for key in ("upfront_payment_dkk", "fees_upfront_dkk", "refundable_deposit_dkk") if offer[key] is None)
    if profile["max_monthly_dkk"] is not None and profile["monthly_budget_basis"] == "LEASE_AND_INSURANCE" and offer["monthly_insurance_dkk"] is None:
        missing.append("monthly_insurance_dkk")

    initial = _money_sum(offer["upfront_payment_dkk"], offer["fees_upfront_dkk"], offer["refundable_deposit_dkk"])
    recurring = _money_sum(offer["monthly_payment_dkk"], offer["monthly_insurance_dkk"] if profile["monthly_budget_basis"] == "LEASE_AND_INSURANCE" else 0)
    return {
        "offer_id": offer["offer_id"],
        "vehicle": offer["vehicle"],
        "calculation_status": "INCOMPLETE_INPUTS" if missing else "CALCULATED_FROM_INPUTS",
        "source_verification": "UNVERIFIED",
        "recommendation": "NOT_ASSESSED",
        "inputs": deepcopy(offer),
        "source": {**deepcopy(source), "age_days": age_days, "expired": expired, "verification": "UNVERIFIED"},
        "economics": {
            "base_contract_cost_dkk": base,
            "average_contract_cost_per_month_dkk": base / offer["term_months"] if base is not None else None,
            "expected_mileage_cost_dkk": econ["total_adjusted_cost"],
            "overage_cost_dkk": econ["overage_cost"] if econ["expected_total_km"] is not None and econ["contracted_total_km"] is not None else None,
            "expected_total_km": econ["expected_total_km"],
            "contracted_total_km": econ["contracted_total_km"],
            "under_mileage_refund_assumed_dkk": 0,
        },
        "budget": {
            "initial_non_monthly": _budget(initial, profile["max_initial_non_monthly_dkk"]),
            "recurring_monthly": {**_budget(recurring, profile["max_monthly_dkk"]), "basis": profile["monthly_budget_basis"]},
        },
        "missing_fields": sorted(set(missing)),
        "warnings": sorted(warnings),
    }


def evaluate_request(request: dict) -> dict:
    """Validate then return a deterministic decision; never a recommendation."""
    normalized = validate_request(request)
    try:
        assessment_day = datetime.strptime(normalized["assessment_at"], "%Y-%m-%dT%H:%M:%SZ").date()
        decision = {
            "schema_version": RESULT_SCHEMA_VERSION,
            "request_schema_version": SCHEMA_VERSION,
            "policy_id": POLICY_ID,
            "canonicalization": CANONICALIZATION_ID,
            "engine_version": __version__,
            "code_sha256": code_fingerprint(),
            "assessment_at": normalized["assessment_at"],
            "normalized_request_sha256": sha256(normalized),
            "confirmed_request_sha256": request_fingerprint(normalized),
            "profile_sha256": profile_fingerprint(normalized["profile"]),
            "profile": normalized["profile"],
            "source_verification": "UNVERIFIED",
            "recommendation": "NOT_ASSESSED",
            "offers": [_evaluate_offer(offer, normalized["profile"], assessment_day) for offer in normalized["offers"]],
            "limitations": list(LIMITATIONS),
        }
        require_finite_tree(decision, "decision")
        canonical_bytes(decision)
        return decision
    except OfferCheckError:
        raise
    except (ArithmeticError, ValueError, TypeError, OSError) as exc:
        raise OfferCheckError("EVALUATION_FAILED", (), 4) from exc


def validate_decision(decision: dict, request: dict) -> dict:
    """Reject a malformed/unbound worker result before CLI publication.

    This is structural and identity checking, not independent arithmetic
    verification. The worker runs the same trusted package in a separate process.
    """
    normalized = validate_request(request)
    try:
        checked = normalize_json(decision)
        schema_path = Path(__file__).with_name("schemas") / "offer-check-result.v1.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))["$defs"]["decision"]
        errors: list[str] = []
        _validate_schema(checked, schema, "$.decision", errors)
        if errors:
            raise OfferCheckError("INVALID_ENGINE_RESULT", errors, 4)
        identity = {
            "engine_version": __version__,
            "code_sha256": code_fingerprint(),
            "normalized_request_sha256": sha256(normalized),
            "confirmed_request_sha256": request_fingerprint(normalized),
            "profile_sha256": profile_fingerprint(normalized["profile"]),
            "assessment_at": normalized["assessment_at"],
            "profile": normalized["profile"],
            "limitations": list(LIMITATIONS),
        }
        if any(checked[key] != value for key, value in identity.items()):
            raise OfferCheckError("ENGINE_IDENTITY_MISMATCH", ("$.decision",), 4)
        if [item["inputs"] for item in checked["offers"]] != normalized["offers"]:
            raise OfferCheckError("ENGINE_IDENTITY_MISMATCH", ("$.decision.offers",), 4)
        if any(item["offer_id"] != item["inputs"]["offer_id"] or item["vehicle"] != item["inputs"]["vehicle"] for item in checked["offers"]):
            raise OfferCheckError("ENGINE_IDENTITY_MISMATCH", ("$.decision.offers",), 4)
        return checked
    except OfferCheckError:
        raise
    except (WireError, ArithmeticError, ValueError, TypeError, KeyError, OSError) as exc:
        raise OfferCheckError("INVALID_ENGINE_RESULT", (), 4) from exc
