"""Unit tests for RBRT Doctor environment and diagnostics module."""

import unittest
from pathlib import Path
from rbrt.doctor import RBRTDoctor

class TestRBRTDoctor(unittest.TestCase):

    def setUp(self):
        self.doctor = RBRTDoctor()

    def test_run_all_returns_valid_checks(self):
        checks = self.doctor.run_all()
        self.assertGreaterEqual(len(checks), 6)
        statuses = {c.status for c in checks}
        # Doctor statuses must be from defined set
        for s in statuses:
            self.assertIn(s, {"PASS", "WARN", "FAIL", "INFO"})

    def test_to_dict_structure(self):
        self.doctor.run_all()
        d = self.doctor.to_dict()
        self.assertIn("toolkit", d)
        self.assertIn("checks", d)
        self.assertIn("summary", d)
        self.assertIn("pass", d["summary"])

    def test_format_text_report(self):
        self.doctor.run_all()
        rep = self.doctor.format_text_report()
        self.assertIn("Audit complete", rep)
