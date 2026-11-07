"""Independent adversarial checks for the public offer transport boundary."""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from copy import deepcopy
from importlib.resources import files
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from glassbox_auto.wire import WireError, canonical_bytes, parse_json_bytes, sha256
from glassbox_auto import cli


@pytest.mark.parametrize(
    "raw",
    [
        b'{"id":1,"id":2}',
        b'{"id":1,"\\u0069d":2}',
        b'{"nested":{"id":1,"id":2}}',
        b'{"x":NaN}',
        b'{"x":Infinity}',
        b'{"x":-Infinity}',
        b'{"x":1e10000}',
        b'{"x":9007199254740992}',
        b'{"x":-9007199254740992}',
        b'{"x":"\\ud800"}',
        b'{"x":"\\udfff"}',
        b'{"\\ud800":1}',
        b'{"x":"\xff"}',
        b'\xef\xbb\xbf{"x":1}',
        b'{"x":1} {"y":2}',
    ],
)
def test_ambiguous_or_unrepresentable_wire_data_is_rejected(raw):
    with pytest.raises(WireError):
        parse_json_bytes(raw)


def test_unicode_is_preserved_without_accidental_equivalence():
    assert parse_json_bytes(b'{"x":"\\ud83d\\ude00"}') == {"x": "😀"}
    assert sha256({"x": "é"}) != sha256({"x": "e\u0301"})
    assert sha256({"x": "A"}) != sha256({"x": "a"})
    assert canonical_bytes({"z": "æ", "a": 1}) == '{"a":1,"z":"æ"}'.encode()


def test_float_zero_is_normalized_but_int_and_float_remain_distinct():
    assert canonical_bytes(parse_json_bytes(b'{"x":-0.0}')) == b'{"x":0.0}'
    assert canonical_bytes({"x": -0.0}) == canonical_bytes({"x": 0.0})
    assert sha256({"x": 1}) != sha256({"x": 1.0})
    assert math.copysign(1, parse_json_bytes(b'-0.0')) == 1


def test_resource_boundaries_include_utf8_bytes_and_object_keys():
    assert parse_json_bytes(json.dumps({"x": "æ" * 4096}).encode()) == {"x": "æ" * 4096}
    for value in ({"x": "æ" * 4097}, {"æ" * 4097: 0}):
        with pytest.raises(WireError, match="JSON_STRING_LIMIT"):
            parse_json_bytes(json.dumps(value).encode())
    with pytest.raises(WireError, match="INPUT_SIZE_LIMIT"):
        parse_json_bytes(b" " * (2 * 1024 * 1024 + 1))


def test_deep_containers_rejected_before_recursive_parse():
    assert parse_json_bytes(b"[" * 32 + b"0" + b"]" * 32)
    with pytest.raises(WireError, match="JSON_DEPTH_LIMIT"):
        parse_json_bytes(b"[" * 33 + b"0" + b"]" * 33)
    # Brackets and escaped quotes inside text are not structural depth.
    assert parse_json_bytes(json.dumps("[" * 100 + '\\"' + "]" * 100).encode())


def test_tree_node_budget_cannot_be_evaded_by_small_scalars():
    with pytest.raises(WireError, match="JSON_NODE_LIMIT"):
        parse_json_bytes(b"[" + b"0," * 100_000 + b"0]")


@pytest.mark.parametrize("value", [float("nan"), float("inf"), {"x": 2**53}, {"x": "\ud800"}])
def test_output_serializer_refuses_invalid_native_values(value):
    with pytest.raises(WireError):
        canonical_bytes(value)


@pytest.mark.parametrize("payload", [b"{}", b'{"decision":"not a decision"}', b"[]", b"NaN"])
def test_malformed_successful_worker_output_is_not_a_calculation(monkeypatch, payload):
    monkeypatch.setattr(
        cli.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, payload, b""),
    )
    with pytest.raises(cli.CLIError) as raised:
        cli._evaluate_with_deadline({})
    assert raised.value.exit_code == 4


def test_output_parent_symlink_swap_does_not_redirect_publication(tmp_path):
    request = tmp_path / "input.json"
    request.write_text("{}")
    intended = tmp_path / "intended"
    intended.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    destination = intended / "result.json"
    cli._preflight(request, destination)
    intended.rename(tmp_path / "original-directory")
    intended.symlink_to(outside, target_is_directory=True)
    try:
        cli._publish_no_overwrite(destination, b"private result")
    except cli.CLIError:
        pass
    assert not (outside / "result.json").exists()


def test_racing_writer_keeps_existing_result_and_removes_tempfiles(tmp_path, monkeypatch):
    output = tmp_path / "result.json"
    real_link = os.link

    def competing_link(source, destination, *args, **kwargs):
        output.write_bytes(b"another writer")
        return real_link(source, destination, *args, **kwargs)

    monkeypatch.setattr(cli.os, "link", competing_link)
    with pytest.raises(cli.CLIError) as raised:
        cli._publish_no_overwrite(output, b"replacement")
    assert raised.value.exit_code == 4
    assert output.read_bytes() == b"another writer"
    assert not list(tmp_path.glob(".glassbox-*"))


def test_published_results_are_private_and_input_hardlinks_are_refused(tmp_path):
    request = tmp_path / "input.json"
    request.write_bytes(b"private input")
    alias = tmp_path / "alias.json"
    os.link(request, alias)
    with pytest.raises(cli.CLIError, match="INPUT_OUTPUT_ALIAS"):
        cli._preflight(request, alias)
    result = tmp_path / "result.json"
    cli._publish_no_overwrite(result, b"private result")
    assert result.stat().st_mode & 0o777 == 0o600
    assert request.read_bytes() == b"private input"


def test_bad_arguments_and_read_paths_do_not_leak_user_text(capfd):
    marker = "SUPER_PRIVATE_INPUT_MARKER"
    assert cli.main(["assess", "/missing/" + marker, "--bad-argument"]) == 2
    out, err = capfd.readouterr()
    assert out == ""
    assert marker not in err
    assert json.loads(err)["error"]["code"] == "INVALID_ARGUMENTS"


def test_timeout_does_not_return_partial_output(monkeypatch):
    def timed_out(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 60, output=b'{"result":"partial"}')

    monkeypatch.setattr(cli.subprocess, "run", timed_out)
    with pytest.raises(cli.CLIError, match="EVALUATION_TIMEOUT") as raised:
        cli._evaluate_with_deadline({})
    assert raised.value.exit_code == 4


def _schema(name):
    schema = json.loads(files("glassbox_auto").joinpath("schemas", name).read_text())
    Draft202012Validator.check_schema(schema)
    return schema


@pytest.mark.parametrize("amount", [0.07, 0.29, 1.14, 9999999.99])
def test_published_schema_accepts_valid_decimal_money(amount):
    schema = _schema("offer-check-request.v1.json")
    field_schema = schema["properties"]["profile"]["properties"]["max_monthly_dkk"]
    assert list(Draft202012Validator(field_schema).iter_errors(amount)) == []


@pytest.mark.parametrize("name", ["complete.json", "incomplete.json", "over-mileage.json"])
def test_packaged_examples_and_actual_cli_results_conform_to_published_schemas(tmp_path, name):
    from glassbox_auto.offer_check import request_fingerprint

    request = json.loads(files("glassbox_auto").joinpath("examples", name).read_text())
    request_schema = _schema("offer-check-request.v1.json")
    request_validator = Draft202012Validator(request_schema, format_checker=FormatChecker())
    request_validator.validate(request)
    request["confirmation"] = {"request_sha256": request_fingerprint(request)}
    request_validator.validate(request)
    input_path = tmp_path / "request.json"
    input_path.write_text(json.dumps(request), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "-m", "glassbox_auto.cli", "assess", str(input_path)],
        cwd=tmp_path, capture_output=True, check=False, timeout=10,
    )
    assert completed.returncode == 0, completed.stderr.decode()
    assert completed.stderr == b""
    result = json.loads(completed.stdout)
    Draft202012Validator(_schema("offer-check-result.v1.json"), format_checker=FormatChecker()).validate(result)
    assert result["decision_payload_sha256"] == sha256(result["decision"])


def test_published_request_schema_rejects_undeclared_policy_injection():
    request = json.loads(files("glassbox_auto").joinpath("examples", "complete.json").read_text())
    request["ignore_missing_fees"] = True
    assert list(Draft202012Validator(_schema("offer-check-request.v1.json")).iter_errors(request))


def _confirmed_example():
    from glassbox_auto.offer_check import request_fingerprint, validate_request

    request = json.loads(files("glassbox_auto").joinpath("examples", "complete.json").read_text())
    normalized = validate_request(request, require_confirmation=False)
    normalized["confirmation"] = {"request_sha256": request_fingerprint(normalized)}
    return normalized


def test_schema_valid_result_for_different_request_is_not_replayed(monkeypatch):
    from glassbox_auto.offer_check import evaluate_request, request_fingerprint

    original = _confirmed_example()
    stale_decision = evaluate_request(original)
    changed = deepcopy(original)
    changed["offers"][0]["monthly_payment_dkk"] += 1
    changed["confirmation"] = {"request_sha256": request_fingerprint(changed)}
    monkeypatch.setattr(
        cli.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, canonical_bytes(stale_decision), b""),
    )
    with pytest.raises(cli.CLIError) as raised:
        cli._evaluate_with_deadline(changed)
    assert raised.value.exit_code == 4


def test_unknown_field_and_invalid_value_errors_do_not_echo_private_material(tmp_path, capfd):
    marker = "PRIVATE_SECRET_DO_NOT_ECHO"
    request = _confirmed_example()
    request["offers"][0]["source"][marker] = marker
    path = tmp_path / "request.json"
    path.write_text(json.dumps(request))
    assert cli.main(["assess", str(path)]) == 2
    out, err = capfd.readouterr()
    assert out == ""
    assert marker not in err
    assert json.loads(err)["error"]["paths"] == ["$.offers[0].source"]


def test_offer_permutation_keeps_confirmed_decision_stable():
    from glassbox_auto.offer_check import evaluate_request, request_fingerprint

    request = _confirmed_example()
    second = deepcopy(request["offers"][0])
    second["offer_id"] = "permuted-second"
    request["offers"].append(second)
    request["confirmation"] = {"request_sha256": request_fingerprint(request)}
    first_decision = evaluate_request(request)
    request["offers"].reverse()
    assert canonical_bytes(evaluate_request(request)) == canonical_bytes(first_decision)

