from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ReleaseIntegrityError(RuntimeError):
    pass


def _resolve_root(root: str | Path | None = None) -> Path:
    candidates = []
    if root is not None:
        candidates.append(Path(root))
    candidates.extend((Path.cwd(), Path(__file__).resolve().parents[2]))

    seen: set[Path] = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if (
            (candidate / "pyproject.toml").is_file()
            and (candidate / "fixtures" / "v3" / "reconstructed_v3_2_1_manifest.json").is_file()
        ):
            return candidate

    searched = ", ".join(str(item) for item in seen)
    raise ReleaseIntegrityError(
        "could not locate repository release metadata; "
        f"searched: {searched}. Pass --root <repo-root> explicitly."
    )


def _load_pyproject(root: Path) -> dict:
    with (root / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)


def _load_manifest(root: Path) -> dict:
    path = root / "fixtures" / "v3" / "reconstructed_v3_2_1_manifest.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def check_release_integrity(
    expected_version: str | None = None,
    root: str | Path | None = None,
) -> list[str]:
    try:
        repo_root = _resolve_root(root)
    except ReleaseIntegrityError as exc:
        return [str(exc)]

    errors: list[str] = []
    project = _load_pyproject(repo_root).get("project", {})
    version = project.get("version")
    if not version:
        errors.append("pyproject.toml has no project.version")
    if expected_version and version != expected_version:
        errors.append(f"package version {version!r} != expected {expected_version!r}")

    manifest = _load_manifest(repo_root)
    required = {
        "schema_version",
        "source_track",
        "artifact",
        "artifact_version",
        "artifact_sha256",
        "base_artifact",
        "base_sha256",
        "revision_a_sha256",
        "patches",
        "catalog_expansion",
        "historical_byte_identity_claim",
        "v3_2_1_parity_verified",
        "remaining_open_conflicts",
    }
    missing = sorted(required - manifest.keys())
    if missing:
        errors.append(f"reconstruction manifest missing fields: {', '.join(missing)}")

    if manifest.get("source_track") != "RECONSTRUCTED_V3_2_1":
        errors.append("3.2.1-R manifest source_track changed")
    if manifest.get("artifact_version") != "3.2.1-R":
        errors.append("3.2.1-R artifact_version changed")
    if manifest.get("catalog_expansion") is not False:
        errors.append("3.2.1-R must remain a compliance patch with catalog_expansion=false")
    if manifest.get("historical_byte_identity_claim") is not False:
        errors.append("historical byte-identity claim must remain false")
    if manifest.get("v3_2_1_parity_verified") is not False:
        errors.append("v3.2.1 parity cannot be marked verified without the historical fixture/harness")

    for field in ("artifact_sha256", "base_sha256", "revision_a_sha256"):
        value = manifest.get(field)
        if not isinstance(value, str) or not HEX64.fullmatch(value):
            errors.append(f"{field} must be a lowercase SHA-256 hex digest")

    patches = manifest.get("patches")
    if not isinstance(patches, list) or not all(isinstance(item, str) and item for item in patches):
        errors.append("patches must be a non-empty list of strings")
    else:
        for required_patch in ("PC-07", "PC-08", "PC-09"):
            if not any(required_patch in item for item in patches):
                errors.append(f"manifest lost required reconstructed patch {required_patch}")

    conflicts = manifest.get("remaining_open_conflicts")
    if not isinstance(conflicts, list) or not any("PC-01" in item for item in conflicts):
        errors.append("PC-01 must remain explicit until an authoritative source resolves it")

    return errors


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GLASSBOX-AUTO release-integrity gate")
    parser.add_argument("--expected-version")
    parser.add_argument("--root", help="Repository root containing pyproject.toml and fixtures/")
    args = parser.parse_args(argv)

    errors = check_release_integrity(args.expected_version, args.root)
    if errors:
        print("RELEASE INTEGRITY: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    repo_root = _resolve_root(args.root)
    version = _load_pyproject(repo_root)["project"]["version"]
    print("RELEASE INTEGRITY: PASS")
    print(f"- package version: {version}")
    print("- 3.2.1-R provenance guard: intact")
    print("- PC-01 unresolved status: explicit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
