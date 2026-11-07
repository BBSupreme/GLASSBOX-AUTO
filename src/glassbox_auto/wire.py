"""Bounded JSON transport and deterministic GBX-PYJSON-1 serialization.

This is deliberately not RFC 8785/JCS. Integers and floats keep their JSON
representation; only negative floating zero is normalized. Text is not folded.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any

MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_OUTPUT_BYTES = 8 * 1024 * 1024
MAX_DEPTH = 32
MAX_NODES = 100_000
MAX_STRING_BYTES = 8_192
MAX_SAFE_INTEGER = 2**53 - 1
SERIALIZER_ID = "GBX-PYJSON-1"


class WireError(ValueError):
    """Sanitized wire error; never includes the offending input value."""

    exit_code = 2

    def __init__(self, code: str, paths: tuple[str, ...] = ()) -> None:
        self.code = code
        self.paths = paths
        super().__init__(code)


def _integer(token: str) -> int:
    # Bound before conversion, including Python's configurable integer limit.
    if len(token.lstrip("-")) > 16:
        raise WireError("UNSAFE_INTEGER")
    result = int(token)
    if abs(result) > MAX_SAFE_INTEGER:
        raise WireError("UNSAFE_INTEGER")
    return result


def _float(token: str) -> float:
    result = float(token)
    if not math.isfinite(result):
        raise WireError("NON_FINITE_NUMBER")
    return 0.0 if result == 0.0 else result


def _constant(_token: str) -> None:
    raise WireError("NON_FINITE_NUMBER")


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise WireError("DUPLICATE_KEY")
        result[key] = value
    return result


def _depth_guard(text: str) -> None:
    """Bound containers before the recursive standard-library JSON parser."""
    depth = 0
    in_string = False
    escaped = False
    for character in text:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
        elif character == '"':
            in_string = True
        elif character in "[{":
            depth += 1
            if depth > MAX_DEPTH:
                raise WireError("JSON_DEPTH_LIMIT")
        elif character in "]}":
            depth -= 1


def normalize_json(value: Any) -> Any:
    """Validate a JSON-native tree and copy it with canonical zero values.

    Object keys count toward the node budget. This conservative counting rule
    also bounds key-heavy payloads. No arbitrary classes or custom encoders run.
    """
    nodes = 0

    def visit(item: Any, depth: int) -> Any:
        nonlocal nodes
        nodes += 1
        if nodes > MAX_NODES:
            raise WireError("JSON_NODE_LIMIT")
        if item is None or type(item) is bool:
            return item
        if type(item) is int:
            if abs(item) > MAX_SAFE_INTEGER:
                raise WireError("UNSAFE_INTEGER")
            return item
        if type(item) is float:
            if not math.isfinite(item):
                raise WireError("NON_FINITE_NUMBER")
            return 0.0 if item == 0.0 else item
        if type(item) is str:
            try:
                encoded = item.encode("utf-8")
            except UnicodeEncodeError as exc:
                raise WireError("INVALID_UNICODE") from exc
            if len(encoded) > MAX_STRING_BYTES:
                raise WireError("JSON_STRING_LIMIT")
            return item
        if type(item) not in (dict, list):
            raise WireError("INVALID_JSON_TYPE")
        depth += 1
        if depth > MAX_DEPTH:
            raise WireError("JSON_DEPTH_LIMIT")
        if type(item) is list:
            return [visit(child, depth) for child in item]
        result = {}
        for key, child in item.items():
            if type(key) is not str:
                raise WireError("INVALID_OBJECT_KEY")
            result[visit(key, depth)] = visit(child, depth)
        return result

    return visit(value, 0)


def parse_json_bytes(raw: bytes, *, max_bytes: int = MAX_INPUT_BYTES) -> Any:
    if type(raw) is not bytes:
        raise WireError("INVALID_INPUT_BYTES")
    if len(raw) > max_bytes:
        raise WireError("INPUT_SIZE_LIMIT")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise WireError("INVALID_UTF8") from exc
    _depth_guard(text)
    try:
        result = json.loads(
            text,
            object_pairs_hook=_object,
            parse_int=_integer,
            parse_float=_float,
            parse_constant=_constant,
        )
    except WireError:
        raise
    except (ValueError, RecursionError) as exc:
        raise WireError("MALFORMED_JSON") from exc
    return normalize_json(result)


def parse_request_bytes(raw: bytes) -> dict[str, Any]:
    result = parse_json_bytes(raw)
    if type(result) is not dict:
        raise WireError("REQUEST_MUST_BE_OBJECT")
    return result


def canonical_bytes(value: Any) -> bytes:
    normalized = normalize_json(value)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()
