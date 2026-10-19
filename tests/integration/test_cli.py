"""Integration tests for all required RBRT CLI subcommands."""

import unittest
import tempfile
import shutil
import io
import sys
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

from rbrt.cli import handle_cli
from tests.fixtures.fixture_generator import create_synthetic_fixtures

class TestCLIIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="rbrt_test_cli_"))
        cls.fixtures = create_synthetic_fixtures(cls.temp_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def _run_cli(self, args: list) -> tuple:
        f_out = io.StringIO()
        f_err = io.StringIO()
        with redirect_stdout(f_out), redirect_stderr(f_err):
            code = handle_cli(args)
        return code, f_out.getvalue(), f_err.getvalue()

    def test_cli_help(self):
        with self.assertRaises(SystemExit) as cm:
            handle_cli(["--help"])
        self.assertEqual(cm.exception.code, 0)

    def test_cli_version(self):
        with self.assertRaises(SystemExit) as cm:
            handle_cli(["--version"])
        self.assertEqual(cm.exception.code, 0)

    def test_cli_doctor_json(self):
        code, out, _ = self._run_cli(["doctor", "--json"])
        self.assertIn('"toolkit": "RogueByte RBRT Toolkit V2"', out)
        self.assertEqual(code, 0)

    def test_cli_device_json(self):
        code, out, _ = self._run_cli(["device", "--json"])
        self.assertIn('"os_name"', out)
        self.assertEqual(code, 0)

    def test_cli_uart_ports(self):
        code, out, _ = self._run_cli(["uart", "ports"])
        self.assertIn("Available Serial Ports", out)
        self.assertEqual(code, 0)

    def test_cli_uart_mock_log(self):
        log_out = self.temp_dir / "cli_uart.log"
        code, out, _ = self._run_cli(["uart", "log", "--port", "MOCK", "--baud", "115200", "--output", str(log_out), "--mock", "--duration", "0.2"])
        self.assertEqual(code, 0)
        self.assertTrue(log_out.exists())

    def test_cli_bin_inspect(self):
        code, out, _ = self._run_cli(["bin", "inspect", str(self.fixtures["bin_a"]), "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"format_hint"', out)

    def test_cli_bin_compare(self):
        code, out, _ = self._run_cli(["bin", "compare", str(self.fixtures["bin_a"]), str(self.fixtures["bin_b"]), "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"differing_bytes_count": 2', out)

    def test_cli_elf_analyze(self):
        code, out, _ = self._run_cli(["elf", "analyze", str(self.fixtures["valid_elf"]), "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"is_valid_elf": true', out)

    def test_cli_elf_compare(self):
        code, out, _ = self._run_cli(["elf", "compare", str(self.fixtures["valid_elf"]), str(self.fixtures["valid_elf"]), "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"arch_match": true', out)

    def test_cli_pup_inspect(self):
        code, out, _ = self._run_cli(["pup", "inspect", str(self.fixtures["pup"]), "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"is_valid_pup_container": true', out)

    def test_cli_pup_compare(self):
        code, out, _ = self._run_cli(["pup", "compare", str(self.fixtures["pup"]), str(self.fixtures["pup"]), "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"binary_identical": true', out)

    def test_cli_dump_inspect(self):
        code, out, _ = self._run_cli(["dump", "inspect", str(self.fixtures["bin_a"]), "--model", "CUH-1215A", "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"device_model": "CUH-1215A"', out)

    def test_cli_report_list(self):
        code, out, _ = self._run_cli(["report", "list"])
        self.assertEqual(code, 0)

    def test_cli_report_export(self):
        code, out, _ = self._run_cli(["report", "export"])
        # Code may be 0 or 1 depending on whether reports exist, but must not crash
        self.assertIn(code, (0, 1))
