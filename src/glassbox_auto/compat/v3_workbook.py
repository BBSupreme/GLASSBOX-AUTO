from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path, PurePosixPath
import zipfile
import xml.etree.ElementTree as ET


RECONSTRUCTED_V3_2_1_SHA256 = "db5d2e8b6429df4229911f6459140ff8d36d8b258609be15a905d4487fc9b972"

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOC_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


@dataclass(frozen=True)
class WorkbookValidation:
    sha256: str
    pc07_offer_gate: bool
    pc08_family_gate: bool
    pc09_terms_gate: bool

    @property
    def passed(self) -> bool:
        return self.pc07_offer_gate and self.pc08_family_gate and self.pc09_terms_gate


def _sheet_member(zf: zipfile.ZipFile, sheet_name: str) -> str:
    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))

    rid = None
    for sheet in workbook.findall(f".//{{{MAIN_NS}}}sheet"):
        if sheet.attrib.get("name") == sheet_name:
            rid = sheet.attrib.get(f"{{{DOC_REL_NS}}}id")
            break
    if not rid:
        raise ValueError(f"sheet not found: {sheet_name}")

    target = None
    for rel in rels.findall(f"{{{PKG_REL_NS}}}Relationship"):
        if rel.attrib.get("Id") == rid:
            target = rel.attrib.get("Target")
            break
    if not target:
        raise ValueError(f"relationship not found for: {sheet_name}")

    normalized = PurePosixPath("xl") / target.lstrip("/")
    if str(normalized).startswith("xl/xl/"):
        normalized = PurePosixPath(str(normalized)[3:])
    return str(normalized)


def _formula(zf: zipfile.ZipFile, sheet_name: str, address: str) -> str:
    root = ET.fromstring(zf.read(_sheet_member(zf, sheet_name)))
    for cell in root.findall(f".//{{{MAIN_NS}}}c"):
        if cell.attrib.get("r") == address:
            formula = cell.find(f"{{{MAIN_NS}}}f")
            if formula is None or not formula.text:
                raise ValueError(f"formula missing at {sheet_name}!{address}")
            return formula.text
    raise ValueError(f"cell not found: {sheet_name}!{address}")


def validate_reconstructed_v3_2_1(
    path: str | Path,
    *,
    expected_sha256: str | None = RECONSTRUCTED_V3_2_1_SHA256,
) -> WorkbookValidation:
    """Validate the generated 3.2.1-R workbook by fingerprint and formula surface.

    `expected_sha256=None` is intended only for validator unit tests or for
    inspecting a newly generated candidate before its fingerprint is pinned.
    Release validation should use the default pinned hash.
    """
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError(f"workbook SHA-256 mismatch: {digest}")

    try:
        with zipfile.ZipFile(path) as zf:
            x5 = _formula(zf, "Scoring_Engine", "X5")
            y5 = _formula(zf, "Scoring_Engine", "Y5")
            z5 = _formula(zf, "Scoring_Engine", "Z5")
    except zipfile.BadZipFile as exc:
        raise ValueError("workbook is not a valid XLSX/ZIP package") from exc

    result = WorkbookValidation(
        sha256=digest,
        pc07_offer_gate=(
            'Offers_Data!Z5="EXPIRED"' in x5
            and 'Offers_Data!Z5="STALE"' in x5
            and 'Offers_Data!Z5="FRESH"' in x5
            and 'Offers_Data!U5="ACTIVE"' in x5
        ),
        pc08_family_gate=("$B$25:$E$25" in y5 and "$B$26:$E$26" not in y5),
        pc09_terms_gate=(
            "'MIN PROFIL'!$G$23" in z5
            and "Offers_Data!AB5" in z5
            and "Offers_Data!AA5" in z5
            and "Offers_Data!AC5" in z5
            and "Offers_Data!AD5" in z5
            and '"UNKNOWN"' in z5
            and '"FAIL"' in z5
            and '"PASS"' in z5
        ),
    )
    if not result.passed:
        raise ValueError(f"workbook compliance surface failed: {result}")
    return result
