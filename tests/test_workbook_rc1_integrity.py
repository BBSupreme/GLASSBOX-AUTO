"""Synthetic package tests; no private workbook is present in public CI."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rc1_checker", ROOT / "scripts/verify_workbook_rc1.py")
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


class WorkbookRC1IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "synthetic.xlsx"

    def fixture(self, cell='<c r="A1"><f>1+1</f><v>2</v></c>'):
        with ZipFile(self.path, "w") as archive:
            archive.writestr("[Content_Types].xml", '<Types/>')
            archive.writestr("xl/workbook.xml", f'<workbook xmlns="{NS}"><sheets><sheet name="Synthetic" sheetId="1"/></sheets></workbook>')
            archive.writestr("xl/worksheets/sheet1.xml", f'<worksheet xmlns="{NS}"><sheetData><row r="1">{cell}</row></sheetData></worksheet>')
        return {"sha256": hashlib.sha256(self.path.read_bytes()).hexdigest(),
                "expected": {"sheets": 1, "formulas": 1, "cached_error_cells": 0}}

    def test_identity_and_counts_do_not_claim_recalculation_or_release(self):
        result = CHECKER.inspect_artifact(self.path, self.fixture())
        self.assertEqual(result["integrity"], "PASS")
        self.assertFalse(result["recalculated"])
        self.assertEqual(result["release_status"], "REVIEW REQUIRED")

    def test_wrong_hash_rejected(self):
        manifest = self.fixture()
        manifest["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA-256 differs"):
            CHECKER.inspect_artifact(self.path, manifest)

    def test_cached_error_rejected(self):
        manifest = self.fixture('<c r="A1" t="e"><f>1/0</f><v>#DIV/0!</v></c>')
        with self.assertRaisesRegex(ValueError, "cached_error_cells"):
            CHECKER.inspect_artifact(self.path, manifest)

    def test_formula_count_rejected(self):
        manifest = self.fixture('<c r="A1"><v>2</v></c>')
        with self.assertRaisesRegex(ValueError, "formulas"):
            CHECKER.inspect_artifact(self.path, manifest)

    def test_sheet_count_rejected(self):
        manifest = self.fixture()
        manifest["expected"]["sheets"] = 2
        with self.assertRaisesRegex(ValueError, "sheets"):
            CHECKER.inspect_artifact(self.path, manifest)

    def test_invalid_package_rejected(self):
        self.path.write_bytes(b"not a zip")
        manifest = {"sha256": hashlib.sha256(self.path.read_bytes()).hexdigest()}
        with self.assertRaisesRegex(ValueError, "Invalid XLSX"):
            CHECKER.inspect_artifact(self.path, manifest)

    def test_rc1_manifest_keeps_review_gates_and_older_track(self):
        manifest = json.loads(CHECKER.MANIFEST.read_text())
        old = json.loads((ROOT / "fixtures/v3/reconstructed_v3_2_1_manifest.json").read_text())
        self.assertEqual(manifest["status"], "REVIEW REQUIRED")
        self.assertEqual(manifest["build_qa"]["excel"], "NOT RUN")
        self.assertTrue(manifest["build_qa"]["fable_5_1"].startswith("NOT RUN"))
        self.assertNotIn(manifest["sha256"], json.dumps(old))
        self.assertEqual(manifest["expected"]["catalogue_rows"], 142)


if __name__ == "__main__":
    unittest.main()
