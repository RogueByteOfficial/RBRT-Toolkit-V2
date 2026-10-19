"""Unit tests for BIN analyzer and chunked comparator."""

import unittest
import hashlib
import tempfile
import shutil
from pathlib import Path

from rbrt.bin_tools.analyzer import inspect_binary_file, compare_binary_files
from tests.fixtures.fixture_generator import create_synthetic_fixtures

class TestBinAnalyzer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="rbrt_test_bin_"))
        cls.fixtures = create_synthetic_fixtures(cls.temp_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_empty_file_inspection(self):
        res = inspect_binary_file(self.fixtures["empty"])
        self.assertEqual(res.size_bytes, 0)
        self.assertEqual(res.sha256, hashlib.sha256(b"").hexdigest())
        self.assertIsNotNone(res.truncation_warning)
        self.assertIn("empty", res.truncation_warning.lower())

    def test_repetitive_filler_detection(self):
        res = inspect_binary_file(self.fixtures["repetitive"])
        self.assertTrue(res.is_repetitive)
        self.assertEqual(res.repetitive_byte, 0xFF)
        self.assertIsNotNone(res.truncation_warning)

    def test_sha256_correctness(self):
        res_a = inspect_binary_file(self.fixtures["bin_a"])
        actual_content = self.fixtures["bin_a"].read_bytes()
        expected_sha = hashlib.sha256(actual_content).hexdigest()
        self.assertEqual(res_a.sha256, expected_sha)

    def test_identical_file_comparison(self):
        res = compare_binary_files(self.fixtures["bin_a"], self.fixtures["bin_a"])
        self.assertTrue(res.identical)
        self.assertEqual(res.differing_bytes_count, 0)
        self.assertEqual(res.differing_percentage, 0.0)
        self.assertIsNone(res.first_diff_offset)

    def test_differing_file_comparison(self):
        res = compare_binary_files(self.fixtures["bin_a"], self.fixtures["bin_b"])
        self.assertFalse(res.identical)
        self.assertEqual(res.differing_bytes_count, 2)
        self.assertEqual(res.first_diff_offset, 100)
        self.assertGreater(len(res.context_diffs), 0)

    def test_large_chunked_file_comparison(self):
        res = compare_binary_files(self.fixtures["large_a"], self.fixtures["large_b"])
        self.assertFalse(res.identical)
        self.assertGreater(res.differing_bytes_count, 0)
        self.assertIsNotNone(res.first_diff_offset)

    def test_nonexistent_file_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            inspect_binary_file(Path("/tmp/nonexistent_rbrt_file.bin"))
