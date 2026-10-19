"""Unit tests for ELF parser, header validation, and diff engine."""

import unittest
import tempfile
import shutil
from pathlib import Path

from rbrt.elf.parser import analyze_elf_file, compare_elf_files
from tests.fixtures.fixture_generator import create_synthetic_fixtures

class TestELFParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="rbrt_test_elf_"))
        cls.fixtures = create_synthetic_fixtures(cls.temp_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_valid_elf64_parsing(self):
        res = analyze_elf_file(self.fixtures["valid_elf"])
        self.assertTrue(res.is_valid_elf)
        self.assertIsNone(res.error)
        self.assertIn("64-bit", res.bitness)
        self.assertIn("x86-64", res.machine_arch)
        self.assertEqual(res.entry_point, "0x00400000")
        self.assertGreater(len(res.sections), 0)
        self.assertGreater(len(res.segments), 0)

    def test_corrupted_truncated_elf(self):
        res = analyze_elf_file(self.fixtures["corrupt_elf"])
        self.assertFalse(res.is_valid_elf)
        self.assertIsNotNone(res.error)
        self.assertGreater(len(res.structural_warnings), 0)

    def test_non_elf_binary_graceful_handling(self):
        res = analyze_elf_file(self.fixtures["repetitive"])
        self.assertFalse(res.is_valid_elf)
        self.assertIn("Magic number mismatch", res.error)

    def test_compare_elf_files(self):
        comp = compare_elf_files(self.fixtures["valid_elf"], self.fixtures["valid_elf"])
        self.assertTrue(comp["arch_match"])
        self.assertTrue(comp["sha256_match"])
        self.assertEqual(comp["modified_sections_count"], 0)
