"""Fixed canonical decisions are shared by every supported Python CI leg.

These are synthetic calculation oracles. Source changes deliberately require a
reviewed fixture refresh; do not regenerate merely to make a failing test green.
"""
import json
from importlib.resources import files
from pathlib import Path

import pytest

from glassbox_auto.offer_check import evaluate_request, request_fingerprint, validate_request
from glassbox_auto.wire import canonical_bytes


@pytest.mark.parametrize("name", ["complete", "incomplete", "over-mileage"])
def test_exact_canonical_decision_matches_release_fixture(name):
    request = json.loads(files("glassbox_auto").joinpath("examples", f"{name}.json").read_text())
    normalized = validate_request(request, require_confirmation=False)
    normalized["confirmation"] = {"request_sha256": request_fingerprint(normalized)}
    decision = evaluate_request(normalized)
    expected = Path(__file__).resolve().parents[1] / "fixtures" / "offer_check" / f"{name}.decision.json"
    assert canonical_bytes(decision) == expected.read_bytes()
