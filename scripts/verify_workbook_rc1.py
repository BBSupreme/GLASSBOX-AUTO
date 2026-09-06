"""Read-only RC1 identity/structure check; not recalculation or release approval."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile


MANIFEST = Path(__file__).resolve().parents[1] / "fixtures/v3/workbook_v3_2_1_rc1_manifest.json"
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def inspect_artifact(path, manifest):
    """Check pinned bytes before XML inspection; return only non-personal counts."""
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest != manifest["sha256"]:
        raise ValueError("Artifact SHA-256 differs from RC1; do not repin to bypass this check")
    try:
        with ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise ValueError("XLSX CRC check failed")
            if "[Content_Types].xml" not in archive.namelist():
                raise ValueError("Missing XLSX content types")
            workbook = ET.fromstring(archive.read("xl/workbook.xml"))
            sheets = len(workbook.findall("s:sheets/s:sheet", NS))
            formulas = errors = 0
            for name in archive.namelist():
                if name.startswith("xl/worksheets/") and name.endswith(".xml"):
                    sheet = ET.fromstring(archive.read(name))
                    formulas += len(sheet.findall(".//s:c/s:f", NS))
                    errors += len(sheet.findall(".//s:c[@t='e']", NS))
    except (BadZipFile, KeyError, ET.ParseError) as exc:
        raise ValueError("Invalid XLSX package") from exc
    actual = {"sheets": sheets, "formulas": formulas, "cached_error_cells": errors}
    for key, value in actual.items():
        if value != manifest["expected"][key]:
            raise ValueError(f"Unexpected {key}: {value}")
    return {"integrity": "PASS", "sha256": digest, **actual,
            "recalculated": False, "release_status": "REVIEW REQUIRED"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    args = parser.parse_args()
    try:
        result = inspect_artifact(args.workbook, json.loads(MANIFEST.read_text()))
    except (OSError, ValueError) as exc:
        # Do not print private paths or workbook values to public CI logs.
        message = str(exc) if isinstance(exc, ValueError) else "Cannot read required local file"
        print(json.dumps({"integrity": "FAIL", "reason": message}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
