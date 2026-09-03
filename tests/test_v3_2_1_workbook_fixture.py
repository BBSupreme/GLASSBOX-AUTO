from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath
import zipfile
import xml.etree.ElementTree as ET


FIXTURE = Path("fixtures/v3/Leasingmatrix_2026_v3.2.1_RECONSTRUCTED.xlsx")
EXPECTED_SHA256 = "db5d2e8b6429df4229911f6459140ff8d36d8b258609be15a905d4487fc9b972"

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOC_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sheet_member(zf: zipfile.ZipFile, sheet_name: str) -> str:
    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))

    rid = None
    for sheet in workbook.findall(f".//{{{MAIN_NS}}}sheet"):
        if sheet.attrib.get("name") == sheet_name:
            rid = sheet.attrib.get(f"{{{DOC_REL_NS}}}id")
            break
    assert rid, f"sheet not found: {sheet_name}"

    target = None
    for rel in rels.findall(f"{{{PKG_REL_NS}}}Relationship"):
        if rel.attrib.get("Id") == rid:
            target = rel.attrib.get("Target")
            break
    assert target, f"relationship not found for: {sheet_name}"

    normalized = PurePosixPath("xl") / target.lstrip("/")
    if str(normalized).startswith("xl/xl/"):
        normalized = PurePosixPath(str(normalized)[3:])
    return str(normalized)


def _formula(zf: zipfile.ZipFile, sheet_name: str, address: str) -> str:
    root = ET.fromstring(zf.read(_sheet_member(zf, sheet_name)))
    for cell in root.findall(f".//{{{MAIN_NS}}}c"):
        if cell.attrib.get("r") == address:
            formula = cell.find(f"{{{MAIN_NS}}}f")
            assert formula is not None and formula.text, f"formula missing at {sheet_name}!{address}"
            return formula.text
    raise AssertionError(f"cell not found: {sheet_name}!{address}")


def test_reconstructed_v3_2_1_fixture_is_fingerprint_pinned():
    assert FIXTURE.exists()
    assert _sha256(FIXTURE) == EXPECTED_SHA256


def test_pc07_expired_offer_fix_is_in_workbook_formula():
    with zipfile.ZipFile(FIXTURE) as zf:
        formula = _formula(zf, "Scoring_Engine", "X5")
    assert 'Offers_Data!Z5="EXPIRED"' in formula
    assert 'Offers_Data!Z5="STALE"' in formula
    assert 'Offers_Data!Z5="FRESH"' in formula
    assert 'Offers_Data!U5="ACTIVE"' in formula


def test_pc08_family_gate_reads_actual_dealbreaker_row():
    with zipfile.ZipFile(FIXTURE) as zf:
        formula = _formula(zf, "Scoring_Engine", "Y5")
    assert "$B$25:$E$25" in formula
    assert "$B$26:$E$26" not in formula


def test_pc09_terms_gate_uses_all_required_operational_inputs():
    with zipfile.ZipFile(FIXTURE) as zf:
        formula = _formula(zf, "Scoring_Engine", "Z5")
    assert "'MIN PROFIL'!$G$23" in formula
    assert "Offers_Data!AB5" in formula
    assert "Offers_Data!AA5" in formula
    assert "Offers_Data!AC5" in formula
    assert "Offers_Data!AD5" in formula
    assert '"UNKNOWN"' in formula
    assert '"FAIL"' in formula
    assert '"PASS"' in formula
