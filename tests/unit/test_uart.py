"""Unit tests for UART serial console, port enumeration, and mock backend."""

import unittest
import tempfile
import shutil
from pathlib import Path

from rbrt.uart.serial_manager import UARTConsole, list_available_ports, MockSerialBackend

class TestUARTManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="rbrt_test_uart_"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_mock_backend_read(self):
        mock = MockSerialBackend(port="MOCK_TEST")
        self.assertTrue(mock.is_open)
        data = mock.read(64)
        self.assertGreater(len(data), 0)
        self.assertIn(b"SBOOT", data)
        mock.close()
        self.assertFalse(mock.is_open)

    def test_uart_console_mock_streaming(self):
        log_out = self.temp_dir / "test_uart.log"
        console = UARTConsole(port="MOCK_DEV", baud=115200, mock_mode=True)
        ok, msg = console.connect()
        self.assertTrue(ok)
        self.assertTrue(console.is_connected)

        stats = console.stream_and_log(output_file=log_out, max_duration_sec=0.5, display=False)
        console.close()

        self.assertGreater(stats["bytes_received"], 0)
        self.assertTrue(log_out.exists())
        log_text = log_out.read_text(encoding="utf-8")
        self.assertIn("SYSCON", log_text)

    def test_port_enumeration_non_crashing(self):
        ports, err = list_available_ports()
        # Should return a list without unhandled exception
        self.assertIsInstance(ports, list)
