"""Unit tests for report generator (JSON, TXT, Markdown)."""

import unittest
import json
import tempfile
import shutil
from pathlib import Path

from rbrt.reports.generator import ReportGenerator

class TestReports(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="rbrt_test_rep_"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_json_report_generation(self):
        rep = ReportGenerator("test_op")
        test_file = self.temp_dir / "target.bin"
        test_file.write_bytes(b"DATA")
        rep.add_input_file(test_file, sha256="abcd", size=4)
        rep.details = {"status": "ok", "samples": [1, 2, 3]}

        out = rep.save(output_format="json", custom_destination=self.temp_dir / "out.json")
        self.assertTrue(out.exists())

        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["metadata"]["operation"], "test_op")
        self.assertEqual(data["metadata"]["toolkit"], "RogueByte RBRT Toolkit V2")
        self.assertEqual(len(data["metadata"]["input_files"]), 1)

    def test_markdown_and_txt_generation(self):
        rep = ReportGenerator("audit")
        rep.add_warning("Sample warning condition")
        rep.add_unsupported_note("Proprietary keys not bundled")

        out_md = rep.save(output_format="md", custom_destination=self.temp_dir / "out.md")
        self.assertTrue(out_md.exists())
        self.assertIn("# RogueByte RBRT Toolkit V2 Report", out_md.read_text(encoding="utf-8"))

        out_txt = rep.save(output_format="txt", custom_destination=self.temp_dir / "out.txt")
        self.assertTrue(out_txt.exists())
        self.assertIn("RogueByte RBRT Toolkit V2", out_txt.read_text(encoding="utf-8"))
