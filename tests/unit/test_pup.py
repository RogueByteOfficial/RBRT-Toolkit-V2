"""Unit tests for PUP firmware inspector and container validator."""

import unittest
import tempfile
import shutil
from pathlib import Path

from rbrt.pup.inspector import inspect_pup_file, compare_pup_files
from tests.fixtures.fixture_generator import create_synthetic_fixtures

class TestPUPInspector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="rbrt_test_pup_"))
        cls.fixtures = create_synthetic_fixtures(cls.temp_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_valid_pup_container_header(self):
        res = inspect_pup_file(self.fixtures["pup"])
        self.assertTrue(res.is_valid_pup_container)
        self.assertIsNone(res.error)
        self.assertEqual(res.package_version, 1)
        self.assertEqual(res.file_entries_count, 1)
        # Verify responsible security: extraction supported is explicitly false for encrypted payloads
        self.assertFalse(res.extraction_supported)
        self.assertTrue(res.encrypted_payload_detected)

    def test_invalid_pup_file(self):
        res = inspect_pup_file(self.fixtures["empty"])
        self.assertFalse(res.is_valid_pup_container)
        self.assertIsNotNone(res.error)

    def test_pup_compare(self):
        comp = compare_pup_files(self.fixtures["pup"], self.fixtures["pup"])
        self.assertTrue(comp["binary_identical"])
        self.assertTrue(comp["both_valid_containers"])
        self.assertEqual(comp["differing_bytes"], 0)
