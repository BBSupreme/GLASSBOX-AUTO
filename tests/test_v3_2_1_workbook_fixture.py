from __future__ import annotations

import json
from pathlib import Path
import zipfile

import pytest

from glassbox_auto.compat.v3_workbook import (
    RECONSTRUCTED_V3_2_1_SHA256,
    validate_reconstructed_v3_2_1,
)


MANIFEST = Path("fixtures/v3/reconstructed_v3_2_1_manifest.json")


def _synthetic_fixture(path: Path) -> None:
    workbook = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
 <sheets><sheet name="Scoring_Engine" sheetId="1" r:id="rId1"/></sheets>
</workbook>'''
    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>'''
    sheet = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="5">
<c r="X5"><f>IF(OR(Offers_Data!Z5="EXPIRED",Offers_Data!Z5="HISTORICAL"),"FAIL",IF(Offers_Data!Z5="STALE","CHECK",IF(AND(Offers_Data!U5="ACTIVE",Offers_Data!Z5="FRESH"),"PASS","UNKNOWN")))</f></c>
<c r="Y5"><f>IF(INDEX(PRØVEKØRSEL!$B$25:$E$25,1,1)="YES","FAIL","PASS")</f></c>
<c r="Z5"><f>IF(OR('MIN PROFIL'!$G$23="",Offers_Data!AB5="",Offers_Data!AA5="",Offers_Data!AC5="",Offers_Data!AD5=""),"UNKNOWN",IF(Offers_Data!AB5&lt;='MIN PROFIL'!$G$23,"PASS","FAIL"))</f></c>
</row></sheetData></worksheet>'''
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet)


def test_reconstruction_manifest_pins_artifact_and_source_track():
    payload = json.loads(MANIFEST.read_text())
    assert payload["source_track"] == "RECONSTRUCTED_V3_2_1"
    assert payload["artifact_version"] == "3.2.1-R"
    assert payload["artifact_sha256"] == RECONSTRUCTED_V3_2_1_SHA256
    assert payload["historical_byte_identity_claim"] is False
    assert payload["v3_2_1_parity_verified"] is False
    assert set(payload["patches"]) == {
        "PC-07 expired active offer gate",
        "PC-08 family Dealbreaker row 25",
        "PC-09 operational lease-terms gate",
    }


def test_workbook_validator_checks_pc07_pc08_pc09_formula_surface(tmp_path):
    fixture = tmp_path / "candidate.xlsx"
    _synthetic_fixture(fixture)
    result = validate_reconstructed_v3_2_1(fixture, expected_sha256=None)
    assert result.passed is True
    assert result.pc07_offer_gate is True
    assert result.pc08_family_gate is True
    assert result.pc09_terms_gate is True


def test_workbook_validator_rejects_non_xlsx(tmp_path):
    candidate = tmp_path / "bad.xlsx"
    candidate.write_bytes(b"not an xlsx")
    with pytest.raises(ValueError, match="valid XLSX"):
        validate_reconstructed_v3_2_1(candidate, expected_sha256=None)


def test_workbook_validator_rejects_wrong_pinned_hash(tmp_path):
    fixture = tmp_path / "candidate.xlsx"
    _synthetic_fixture(fixture)
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        validate_reconstructed_v3_2_1(fixture, expected_sha256="0" * 64)
