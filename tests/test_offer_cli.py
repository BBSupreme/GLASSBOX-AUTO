"""Transport/command regressions; numbers come from the separate core suite."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from glassbox_auto import cli
from glassbox_auto.wire import (
    MAX_INPUT_BYTES,
    MAX_SAFE_INTEGER,
    WireError,
    canonical_bytes,
    parse_request_bytes,
    sha256,
)


def draft_request():
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
        "offers": [{
            "offer_id": "synthetic-a",
            "vehicle": "Synthetic family EV A",
            "mode": "LEASE_NEW",
            "currency": "DKK",
            "source": {
                "kind": "SYNTHETIC",
                "locator": "Synthetic example; not a market offer",
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
            "mandatory_fees_dkk": 600,
            "fees_upfront_dkk": 0,
            "refundable_deposit_dkk": 0,
            "monthly_insurance_dkk": 500,
            "overage_dkk_per_km": 1.5,
        }],
    }


def confirmed_request():
    from glassbox_auto.offer_check import request_fingerprint, validate_request

    request = validate_request(draft_request(), require_confirmation=False)
    request["confirmation"] = {"request_sha256": request_fingerprint(request)}
    return request


def run_cli(*arguments, cwd=None):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    return subprocess.run(
        [sys.executable, "-m", "glassbox_auto.cli", *map(str, arguments)],
        capture_output=True, check=False, env=environment, cwd=cwd, timeout=10,
    )


@pytest.mark.parametrize("raw,code", [
    (b'{"a":1,"a":2}', "DUPLICATE_KEY"),
    (b'{"a":{"x":1,"x":2}}', "DUPLICATE_KEY"),
    (b'{"value":NaN}', "NON_FINITE_NUMBER"),
    (b'{"value":Infinity}', "NON_FINITE_NUMBER"),
    (b'{"value":-Infinity}', "NON_FINITE_NUMBER"),
    (b'{"value":1e309}', "NON_FINITE_NUMBER"),
    (b'{"value":9007199254740992}', "UNSAFE_INTEGER"),
    (b'{"value":-9007199254740992}', "UNSAFE_INTEGER"),
    (b'{"value":"\\ud800"}', "INVALID_UNICODE"),
    (b'{"\\udfff":1}', "INVALID_UNICODE"),
    (b'{"value":"\xff"}', "INVALID_UTF8"),
    (b'\xef\xbb\xbf{}', "MALFORMED_JSON"),
    (b'[]', "REQUEST_MUST_BE_OBJECT"),
    (b'{"value":}', "MALFORMED_JSON"),
    (b'{} trailing', "MALFORMED_JSON"),
])
def test_strict_json_rejects_ambiguous_wire(raw, code):
    with pytest.raises(WireError) as caught:
        parse_request_bytes(raw)
    assert caught.value.code == code


def test_canonical_transport_has_exact_supported_semantics():
    request = parse_request_bytes(b'{"z":-0.0,"b":1.0,"a":1,"x":"\\ud83d\\ude00"}')
    assert canonical_bytes(request) == '{"a":1,"b":1.0,"x":"😀","z":0.0}'.encode()
    assert sha256({"b": 2, "a": 1}) == sha256({"a": 1, "b": 2})
    assert sha256({"x": 1}) != sha256({"x": 1.0})
    assert sha256({"x": "é"}) != sha256({"x": "e\u0301"})
    assert parse_request_bytes(f'{{"x":{MAX_SAFE_INTEGER}}}'.encode())["x"] == MAX_SAFE_INTEGER


def test_depth_guard_ignores_escaped_quotes_and_braces_in_strings():
    assert parse_request_bytes(json.dumps({"x": '[{"' * 200}).encode()) == {"x": '[{"' * 200}
    with pytest.raises(WireError, match="JSON_DEPTH_LIMIT"):
        parse_request_bytes(("[" * 33 + "0" + "]" * 33).encode())


def test_wire_resource_limits_are_explicit():
    with pytest.raises(WireError, match="INPUT_SIZE_LIMIT"):
        parse_request_bytes(b" " * (MAX_INPUT_BYTES + 1))
    with pytest.raises(WireError, match="JSON_STRING_LIMIT"):
        parse_request_bytes(json.dumps({"x": "a" * 8193}).encode())
    with pytest.raises(WireError, match="JSON_NODE_LIMIT"):
        parse_request_bytes(b'{"x":[' + b'0,' * 99999 + b'0]}')


def test_prepare_exposes_inputs_and_confirmed_execution_hashes(tmp_path):
    source = tmp_path / "request.json"
    source.write_text(json.dumps(draft_request()))
    prepared = run_cli("prepare", source)
    assert prepared.returncode == 0, prepared.stderr
    preview = json.loads(prepared.stdout)
    assert preview["status"] == "AWAITING_CONFIRMATION"
    assert "confirmation" not in preview["request"]
    assert preview["request"]["profile"] == draft_request()["profile"]

    preview["request"]["confirmation"] = {"request_sha256": preview["request_sha256"]}
    raw = json.dumps(preview["request"]).encode()
    source.write_bytes(raw)
    executed = run_cli("assess", source)
    assert executed.returncode == 0, executed.stderr
    envelope = json.loads(executed.stdout)
    assert set(envelope) == {"decision", "decision_payload_sha256", "transport"}
    assert envelope["transport"]["raw_request_sha256"] == hashlib.sha256(raw).hexdigest()
    assert envelope["decision_payload_sha256"] == sha256(envelope["decision"])
    assert "raw_request_sha256" not in envelope["decision"]


def test_transport_whitespace_changes_only_raw_hash(tmp_path):
    source = tmp_path / "request.json"
    request = confirmed_request()
    source.write_text(json.dumps(request, indent=2))
    first = run_cli("assess", source)
    source.write_bytes(canonical_bytes(request))
    second = run_cli("assess", source)
    assert first.returncode == second.returncode == 0
    left, right = json.loads(first.stdout), json.loads(second.stdout)
    assert left["transport"] != right["transport"]
    assert left["decision"] == right["decision"]
    assert left["decision_payload_sha256"] == right["decision_payload_sha256"]


def test_modified_offer_invalidates_whole_request_confirmation(tmp_path):
    request = confirmed_request()
    request["offers"][0]["monthly_payment_dkk"] += 1
    source = tmp_path / "request.json"
    source.write_text(json.dumps(request))
    executed = run_cli("assess", source)
    assert executed.returncode == 2
    assert executed.stdout == b""
    assert "confirmation" in json.loads(executed.stderr)["error"]["paths"][0]


def test_no_output_file_is_overwritten_and_aliases_fail(tmp_path):
    source, output = tmp_path / "request.json", tmp_path / "result.json"
    source.write_text(json.dumps(confirmed_request()))
    first = run_cli("assess", source, "--output", output)
    assert first.returncode == 0, first.stderr
    assert first.stdout == b""
    original = output.read_bytes()
    second = run_cli("assess", source, "--output", output)
    assert second.returncode == 2
    assert second.stdout == b""
    assert output.read_bytes() == original
    assert run_cli("assess", source, "--output", source).returncode == 2
    alias = tmp_path / "alias.json"
    os.link(source, alias)
    assert run_cli("assess", source, "--output", alias).returncode == 2
    assert not list(tmp_path.glob(".glassbox-*"))


def test_symlinks_and_fifos_do_not_get_read(tmp_path):
    source = tmp_path / "request.json"
    source.write_text(json.dumps(confirmed_request()))
    alias = tmp_path / "symlink.json"
    alias.symlink_to(source)
    assert run_cli("assess", alias).returncode == 2
    output = tmp_path / "dangling.json"
    output.symlink_to(tmp_path / "missing.json")
    assert run_cli("assess", source, "--output", output).returncode == 2
    if hasattr(os, "mkfifo"):
        fifo = tmp_path / "fifo"
        os.mkfifo(fifo)
        assert run_cli("assess", fifo).returncode == 2


def test_atomic_publication_rejects_concurrent_writer(tmp_path, monkeypatch):
    output = tmp_path / "result.json"
    actual_link = os.link

    def racing_link(src, dst, **kwargs):
        output.write_bytes(b"concurrent writer")
        return actual_link(src, dst, **kwargs)

    monkeypatch.setattr(cli.os, "link", racing_link)
    with pytest.raises(cli.CLIError) as caught:
        cli._publish_no_overwrite(output, b"new result")
    assert caught.value.exit_code == 4
    assert output.read_bytes() == b"concurrent writer"
    assert not list(tmp_path.glob(".glassbox-*"))


def test_evaluation_timeout_fails_closed(monkeypatch):
    def time_out(*args, **kwargs):
        assert kwargs["timeout"] == 60
        assert "-I" in args[0]
        raise subprocess.TimeoutExpired("ignored", 60)

    monkeypatch.setattr(cli.subprocess, "run", time_out)
    with pytest.raises(cli.CLIError) as caught:
        cli._evaluate_with_deadline({})
    assert (caught.value.exit_code, caught.value.code) == (4, "EVALUATION_TIMEOUT")


def test_invalid_arguments_and_worker_failures_do_not_echo_input(tmp_path, monkeypatch):
    secret = "PRIVATE_TOKEN_DO_NOT_PRINT"
    invalid = run_cli("assess", f"/nonexistent/{secret}")
    assert invalid.returncode == 2
    assert secret.encode() not in invalid.stderr
    assert invalid.stdout == b""
    typo = run_cli(secret)
    assert typo.returncode == 2
    assert secret.encode() not in typo.stderr

    monkeypatch.setattr(cli.subprocess, "run", lambda *a, **kw: subprocess.CompletedProcess([], 1, b"", secret.encode()))
    with pytest.raises(cli.CLIError) as caught:
        cli._evaluate_with_deadline({})
    assert str(caught.value) == "EVALUATION_FAILED"


def test_help_version_are_accessible():
    assert b"prepare" in run_cli("--help").stdout
    assert run_cli("--version").returncode == 0
