from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "fixtures" / "v3" / "reconstructed_v3_2_1_manifest.json"
PYPROJECT = ROOT / "pyproject.toml"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ReleaseIntegrityError(RuntimeError):
    pass


def _load_pyproject() -> dict:
    with PYPROJECT.open("rb") as fh:
        return tomllib.load(fh)


def _load_manifest() -> dict:
    with MANIFEST.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def check_release_integrity(expected_version: str | None = None) -> list[str]:
    errors: list[str] = []
    project = _load_pyproject().get("project", {})
    version = project.get("version")
    if not version:
        errors.append("pyproject.toml has no project.version")
    if expected_version and version != expected_version:
        errors.append(f"package version {version!r} != expected {expected_version!r}")

    manifest = _load_manifest()
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
    args = parser.parse_args(argv)
    errors = check_release_integrity(args.expected_version)
    if errors:
        print("RELEASE INTEGRITY: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RELEASE INTEGRITY: PASS")
    print(f"- package version: {_load_pyproject()['project']['version']}")
    print("- 3.2.1-R provenance guard: intact")
    print("- PC-01 unresolved status: explicit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
