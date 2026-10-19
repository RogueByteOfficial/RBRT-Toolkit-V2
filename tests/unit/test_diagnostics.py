"""Unit tests for diagnostic log parsing and error code mapping."""

import unittest
import tempfile
import shutil
from pathlib import Path

from rbrt.diagnostics.log_analyzer import DiagnosticLogAnalyzer
from tests.fixtures.fixture_generator import create_synthetic_fixtures

class TestDiagnostics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="rbrt_test_diag_"))
        cls.fixtures = create_synthetic_fixtures(cls.temp_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_log_analysis_patterns(self):
        analyzer = DiagnosticLogAnalyzer()
        res = analyzer.analyze_file(self.fixtures["log"])
        self.assertGreater(res["anomalies_detected"], 0)
        severities = res["severity_summary"]
        self.assertGreater(severities["CRITICAL"] + severities["ERROR"], 0)

        # Check that Syscon code 80801500 has description
        matches = res["matches"]
        syscon_matches = [m for m in matches if "80801500" in (m.get("code") or "")]
        self.assertGreater(len(syscon_matches), 0)

    def test_repeated_message_grouping(self):
        analyzer = DiagnosticLogAnalyzer()
        res = analyzer.analyze_file(self.fixtures["log"])
        freq = res["frequent_messages"]
        self.assertGreater(len(freq), 0)
        self.assertTrue(any("Repeated event message" in item["pattern"] for item in freq))
