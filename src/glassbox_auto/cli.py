"""Offline, bounded command interface for the concrete leasing-offer checker."""
from __future__ import annotations

import argparse
import hashlib
from importlib import resources
import os
from pathlib import Path
import secrets
import stat
import subprocess
import sys
from typing import Any

from . import __version__
from .wire import (
    MAX_INPUT_BYTES,
    MAX_OUTPUT_BYTES,
    WireError,
    canonical_bytes,
    parse_json_bytes,
    parse_request_bytes,
    sha256,
)

EVALUATION_TIMEOUT_SECONDS = 60


class CLIError(ValueError):
    def __init__(self, code: str, exit_code: int = 2, paths: tuple[str, ...] = ()) -> None:
        self.code = code
        self.exit_code = exit_code
        self.paths = paths
        super().__init__(code)


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, _message: str) -> None:
        # argparse's default prints user input. Keep failure output machine-safe.
        raise CLIError("INVALID_ARGUMENTS")


def _parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(
        prog="glassbox-auto",
        description="Check dated private-leasing offers offline. Costs are conditional on supplied inputs.",
        epilog="No network retrieval, purchase support, vehicle ranking, or verification of source truth.",
    )
    parser.add_argument("--version", action="version", version=f"glassbox-auto {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    example = commands.add_parser("example", help="Print a synthetic draft request; it is not a current market offer.")
    example.add_argument("--name", choices=("complete", "incomplete", "over-mileage"), default="complete")
    for command, help_text in (
        ("prepare", "Validate and display all inputs and the hash to confirm before calculation."),
        ("assess", "Calculate confirmed inputs; exit 0 means execution, not a recommendation."),
    ):
        subparser = commands.add_parser(command, help=help_text, description=help_text)
        subparser.add_argument("request", help="UTF-8 JSON request file (maximum 2 MiB).")
        subparser.add_argument("--output", help="Publish JSON to a new path atomically; existing files are refused.")
    return parser


def _reject_symlink_components(path: Path) -> None:
    # Do not resolve away symlinks before checking them, including link/../file.
    absolute = path if path.is_absolute() else Path.cwd() / path
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        try:
            if stat.S_ISLNK(os.lstat(current).st_mode):
                raise CLIError("SYMLINK_PATH_NOT_ALLOWED")
        except FileNotFoundError:
            # The final output filename may not exist. A missing parent is
            # rejected separately before any evaluation starts.
            continue


def _preflight(input_path: Path, output_path: Path | None) -> None:
    try:
        _reject_symlink_components(input_path)
        if not stat.S_ISREG(input_path.stat().st_mode):
            raise CLIError("INPUT_NOT_REGULAR_FILE")
        if output_path is None:
            return
        _reject_symlink_components(output_path)
        if os.path.lexists(output_path):
            if os.path.samefile(input_path, output_path):
                raise CLIError("INPUT_OUTPUT_ALIAS")
            raise CLIError("OUTPUT_ALREADY_EXISTS")
        if not output_path.parent.is_dir():
            raise CLIError("OUTPUT_PARENT_NOT_DIRECTORY")
    except CLIError:
        raise
    except OSError as exc:
        raise CLIError("INPUT_OUTPUT_UNAVAILABLE") from exc


def _open_directory(path: Path) -> int:
    """Anchor every directory component without following any symlink.

    The file-output option requires POSIX directory-fd primitives. Other
    platforms can still use JSON on stdout rather than a weaker file writer.
    """
    if not hasattr(os, "O_DIRECTORY") or os.open not in os.supports_dir_fd:
        raise CLIError("SAFE_FILE_OUTPUT_UNSUPPORTED", 4)
    flags = os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
    absolute = path if path.is_absolute() else Path.cwd() / path
    descriptor = os.open(absolute.anchor, flags)
    try:
        for part in absolute.parts[1:]:
            next_descriptor = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _read_input(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    parent_fd = None
    try:
        if hasattr(os, "O_DIRECTORY") and os.open in os.supports_dir_fd:
            parent_fd = _open_directory(path.parent)
            descriptor = os.open(path.name, flags, dir_fd=parent_fd)
        else:
            descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise CLIError("INPUT_NOT_REGULAR_FILE")
            raw = stream.read(MAX_INPUT_BYTES + 1)
    except CLIError:
        raise
    except OSError as exc:
        raise CLIError("INPUT_UNREADABLE") from exc
    finally:
        if parent_fd is not None:
            os.close(parent_fd)
    if len(raw) > MAX_INPUT_BYTES:
        raise WireError("INPUT_SIZE_LIMIT")
    return raw


def _diagnostic(error: Exception) -> dict[str, Any]:
    # Codes and paths are package-defined metadata, never exception messages.
    code = getattr(error, "code", "INTERNAL_ERROR")
    paths = getattr(error, "paths", ())
    if not isinstance(code, str) or not code.replace("_", "").isalnum() or len(code) > 80:
        code = "INTERNAL_ERROR"
    safe_paths = sorted({
        path for path in paths
        if isinstance(path, str) and len(path) <= 256
        and all(character.isascii() and (character.isalnum() or character in "_.[]-$/") for character in path)
    }) if isinstance(paths, (tuple, list)) else []
    return {"error": {"code": code, "paths": safe_paths}}


def _emit_error(error: Exception) -> int:
    exit_code = getattr(error, "exit_code", 4)
    if exit_code not in (2, 3, 4, 5, 6):
        exit_code = 4
    sys.stderr.write(canonical_bytes(_diagnostic(error)).decode("utf-8") + "\n")
    return exit_code


def _worker() -> int:
    """Private subprocess target; only package code consumes the request."""
    try:
        from .offer_check import evaluate_request

        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        request = parse_request_bytes(raw)
        decision = evaluate_request(request)
        try:
            encoded = canonical_bytes(decision)
        except WireError as exc:
            raise CLIError("INVALID_ENGINE_OUTPUT", 4) from exc
        if len(encoded) > MAX_OUTPUT_BYTES:
            raise CLIError("OUTPUT_SIZE_LIMIT", 4)
        sys.stdout.buffer.write(encoded)
        return 0
    except Exception as exc:
        return _emit_error(exc)


def _evaluate_with_deadline(request: dict[str, Any]) -> dict[str, Any]:
    # Load the same trusted package selected by the parent, including source
    # checkouts. Isolated Python ignores ambient PYTHONPATH/user-site modules
    # and prevents a second package in the working directory shadowing it.
    package_root = str(Path(__file__).resolve().parent.parent)
    worker_code = (
        f"import sys; sys.path.insert(0, {package_root!r}); "
        "from glassbox_auto.cli import _worker; raise SystemExit(_worker())"
    )
    try:
        completed = subprocess.run(
            [sys.executable, "-I", "-c", worker_code],
            input=canonical_bytes(request),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=EVALUATION_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise CLIError("EVALUATION_TIMEOUT", 4) from exc
    except OSError as exc:
        raise CLIError("EVALUATION_UNAVAILABLE", 4) from exc
    if completed.returncode:
        # Re-emit only the closed diagnostic shape, never a traceback or raw
        # subprocess stderr. Broken workers fail as internal errors.
        try:
            diagnostic = parse_json_bytes(completed.stderr)
            if set(diagnostic) != {"error"} or set(diagnostic["error"]) != {"code", "paths"}:
                raise ValueError
            error = diagnostic["error"]
            raise CLIError(error["code"], completed.returncode, tuple(error["paths"]))
        except CLIError:
            raise
        except Exception as exc:
            raise CLIError("EVALUATION_FAILED", 4) from exc
    if len(completed.stdout) > MAX_OUTPUT_BYTES:
        raise CLIError("OUTPUT_SIZE_LIMIT", 4)
    try:
        decision = parse_json_bytes(completed.stdout, max_bytes=MAX_OUTPUT_BYTES)
    except WireError as exc:
        raise CLIError("INVALID_ENGINE_OUTPUT", 4) from exc
    if type(decision) is not dict:
        raise CLIError("INVALID_ENGINE_OUTPUT", 4)
    try:
        from .offer_check import validate_decision

        validate_decision(decision, request)
    except Exception as exc:
        raise CLIError("INVALID_ENGINE_OUTPUT", 4) from exc
    return decision


def _publish_no_overwrite(path: Path, payload: bytes, *, directory_fd: int | None = None) -> None:
    """Publish a private temporary file using atomic hard-link no-clobber.

    Hard-link publication is deliberately required. Filesystems without this
    facility fail explicitly rather than falling back to overwrite-prone rename.
    """
    temporary: str | None = None
    owned_directory_fd = directory_fd is None
    try:
        # A standalone call opens safely now. The command opens before
        # evaluation and retains that descriptor until publication completes.
        if directory_fd is None:
            directory_fd = _open_directory(path.parent)
        check_fd = _open_directory(path.parent)
        try:
            anchored = os.fstat(directory_fd)
            current = os.fstat(check_fd)
            if (anchored.st_dev, anchored.st_ino) != (current.st_dev, current.st_ino):
                raise CLIError("OUTPUT_DIRECTORY_CHANGED", 4)
        finally:
            os.close(check_fd)
        temporary = f".glassbox-{secrets.token_hex(16)}"
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=directory_fd,
        )
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(
            temporary, path.name,
            src_dir_fd=directory_fd, dst_dir_fd=directory_fd, follow_symlinks=False,
        )
    except OSError as exc:
        raise CLIError("OUTPUT_PUBLICATION_FAILED", 4) from exc
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary, dir_fd=directory_fd)
            except OSError:
                pass
        if owned_directory_fd and directory_fd is not None:
            os.close(directory_fd)


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if arguments == ["_worker"]:
        return _worker()
    output_directory_fd = None
    try:
        options = _parser().parse_args(arguments)
        if options.command == "example":
            resource = resources.files("glassbox_auto").joinpath("examples", f"{options.name}.json")
            example = parse_request_bytes(resource.read_bytes())
            sys.stdout.buffer.write(canonical_bytes(example) + b"\n")
            return 0
        input_path = Path(options.request)
        output_path = Path(options.output) if options.output is not None else None
        _preflight(input_path, output_path)
        if output_path is not None:
            try:
                output_directory_fd = _open_directory(output_path.parent)
            except OSError as exc:
                raise CLIError("OUTPUT_PARENT_UNAVAILABLE") from exc
        raw = _read_input(input_path)
        request = parse_request_bytes(raw)
        if options.command == "prepare":
            from .offer_check import request_fingerprint, validate_request

            normalized = validate_request(request, require_confirmation=False)
            review_request = {key: value for key, value in normalized.items() if key != "confirmation"}
            result = {
                "status": "AWAITING_CONFIRMATION",
                "request_sha256": request_fingerprint(normalized),
                "request": review_request,
                "notice": (
                    "Review every input with the user before copying request_sha256 into "
                    "confirmation.request_sha256. A matching hash detects changed inputs; "
                    "it does not authenticate consent or verify source truth."
                ),
            }
        else:
            decision = _evaluate_with_deadline(request)
            result = {
                "decision": decision,
                "decision_payload_sha256": sha256(decision),
                "transport": {"raw_request_sha256": hashlib.sha256(raw).hexdigest()},
            }
        try:
            payload = canonical_bytes(result)
        except WireError as exc:
            raise CLIError("INVALID_OUTPUT", 4) from exc
        if len(payload) > MAX_OUTPUT_BYTES:
            raise CLIError("OUTPUT_SIZE_LIMIT", 4)
        if output_path is None:
            sys.stdout.buffer.write(payload + b"\n")
        else:
            _publish_no_overwrite(output_path, payload, directory_fd=output_directory_fd)
        return 0
    except (KeyboardInterrupt, BrokenPipeError):
        return _emit_error(CLIError("EXECUTION_INTERRUPTED", 4))
    except Exception as exc:
        return _emit_error(exc)
    finally:
        if output_directory_fd is not None:
            os.close(output_directory_fd)


if __name__ == "__main__":
    raise SystemExit(main())
