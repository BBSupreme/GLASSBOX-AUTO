"""Exercise an installed wheel outside the checkout, using synthetic inputs only.

Run with the clean wheel environment's Python. Never use this automated synthetic
confirmation helper to bypass a person's confirmation of a real quote.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def main():
    with tempfile.TemporaryDirectory(prefix="gbx-wheel-smoke-") as directory:
        root = Path(directory)
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)

        def run(*args, expected=0):
            completed = subprocess.run(
                [sys.executable, "-I", "-m", "glassbox_auto.cli", *args],
                cwd=root, env=env, capture_output=True, timeout=65,
            )
            assert completed.returncode == expected, (args, completed.returncode, completed.stderr.decode())
            if expected:
                assert not completed.stdout, "failed commands must not emit success output"
                return json.loads(completed.stderr)
            assert not completed.stderr, completed.stderr.decode()
            return json.loads(completed.stdout) if completed.stdout else None

        # Every example and schema must be available through the installed wheel.
        from importlib.resources import files
        from importlib.metadata import version
        assert version("glassbox-auto") == "0.3.0"
        schemas = files("glassbox_auto").joinpath("schemas")
        for filename in ("offer-check-request.v1.json", "offer-check-result.v1.json"):
            assert json.loads(schemas.joinpath(filename).read_text())["$schema"]

        for name in ("complete", "incomplete", "over-mileage"):
            request = run("example", "--name", name)
            assert all(offer["source"]["kind"] == "SYNTHETIC" for offer in request["offers"])
            request_path = root / f"{name}.json"
            request_path.write_bytes(canonical(request))
            preparation = run("prepare", str(request_path))
            assert preparation["status"] == "AWAITING_CONFIRMATION"
            request["confirmation"] = {"request_sha256": preparation["request_sha256"]}
            request_path.write_bytes(canonical(request))
            result = run("assess", str(request_path))
            decision = result["decision"]
            assert result["decision_payload_sha256"] == hashlib.sha256(canonical(decision)).hexdigest()
            assert result["transport"]["raw_request_sha256"] == hashlib.sha256(request_path.read_bytes()).hexdigest()
            assert decision["engine_version"] == "0.3.0"
            assert decision["confirmed_request_sha256"] == preparation["request_sha256"]
            assert decision["source_verification"] == "UNVERIFIED"
            assert decision["recommendation"] == "NOT_ASSESSED"
            offer = decision["offers"][0]
            if name == "incomplete":
                assert offer["economics"]["base_contract_cost_dkk"] is None
                assert offer["budget"]["recurring_monthly"]["status"] == "UNKNOWN"
            else:
                assert offer["economics"]["base_contract_cost_dkk"] == 141600
                assert offer["budget"]["initial_non_monthly"]["amount_dkk"] == 15000
                assert offer["budget"]["recurring_monthly"]["amount_dkk"] == 4000
            if name == "over-mileage":
                assert offer["economics"]["overage_cost_dkk"] == 45000
                assert offer["economics"]["expected_mileage_cost_dkk"] == 186600
                assert "OFFER_EXPIRED" in offer["warnings"]
                assert "SOURCE_CONFLICT_UNRESOLVED" in offer["warnings"]

            # Different transport formatting must not change the decision.
            request_path.write_text(json.dumps(request, indent=4, ensure_ascii=False), encoding="utf-8")
            formatted = run("assess", str(request_path))
            assert formatted["decision"] == decision
            assert formatted["transport"] != result["transport"]

            destination = root / f"{name}-result.json"
            run("assess", str(request_path), "--output", str(destination))
            saved = destination.read_bytes()
            run("assess", str(request_path), "--output", str(destination), expected=2)
            assert destination.read_bytes() == saved
            request["profile"]["expected_annual_km"] += 1
            request_path.write_bytes(canonical(request))
            error = run("assess", str(request_path), expected=2)
            assert error["error"]["code"] == "CONFIRMATION_MISMATCH"
            print(f"installed-wheel {name}: PASS; decision SHA-256 {result['decision_payload_sha256']}")


if __name__ == "__main__":
    main()
