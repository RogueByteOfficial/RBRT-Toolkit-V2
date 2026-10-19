"""UART serial console management, port enumeration, safe logging, and mock backend for automated testing."""

import sys
import time
import glob
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any

from rbrt.utils.styling import styler

# Try importing serial and list_ports
try:
    import serial
    import serial.tools.list_ports
    _HAS_PYSERIAL = True
except ImportError:
    _HAS_PYSERIAL = False


HARDWARE_SAFETY_NOTICE = """
[!] HARDWARE VOLTAGE & SAFETY WARNING:
  • Console logic levels are 1.8V or 3.3V (e.g., PS4/PS5 Southbridge/Syscon).
  • NEVER connect 5V TTL logic directly to low-voltage console test points (causes permanent damage).
  • Verify common ground connection BEFORE powering on host or target.
  • Initial UART capture must remain READ-ONLY (do not transmit commands unless protocol is verified).
  • Board revisions (e.g. SAA-001, SAB-001, SAC-001, EDM-010/020) have different test-point layouts.
"""

class MockSerialBackend:
    """Mock serial device backend for automated testing and hardware-free simulation."""

    def __init__(self, port: str = "MOCK_PORT", baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_open = True
        self.buffer = (
            b"[00000.000] SBOOT: Initializing Southbridge Bootloader v2.10\r\n"
            b"[00000.045] SECURE_BOOT: Verification of BL2 stage completed\r\n"
            b"[00000.120] SYSCON: Response OK, Core voltage nominal at 1.15V\r\n"
            b"[00000.250] DDR4: Memory training completed, 8GB detected\r\n"
            b"[00000.410] ERR: Thermal prober offset +1.4C on bank 0 (INFO)\r\n"
            b"[00000.600] KERNEL: Loading primary payload...\r\n"
        )
        self.read_pointer = 0

    def read(self, size: int = 64) -> bytes:
        if not self.is_open or self.read_pointer >= len(self.buffer):
            time.sleep(0.05)
            return b""
        chunk = self.buffer[self.read_pointer:self.read_pointer + size]
        self.read_pointer += len(chunk)
        return chunk

    def write(self, data: bytes) -> int:
        return len(data)

    def close(self) -> None:
        self.is_open = False


def list_available_ports() -> Tuple[List[Dict[str, str]], Optional[str]]:
    """Lists available serial ports using pySerial or OS-level device scan."""
    ports: List[Dict[str, str]] = []

    if _HAS_PYSERIAL:
        try:
            detected = serial.tools.list_ports.comports()
            for p in detected:
                ports.append({
                    "device": p.device,
                    "description": p.description or "Generic Serial Port",
                    "hwid": p.hwid or "N/A"
                })
            return ports, None
        except Exception as e:
            return [], f"pySerial port query error: {e}"

    # Fallback to direct Linux/Unix /dev/tty* scan
    if sys.platform.startswith("linux"):
        for pattern in ["/dev/ttyUSB*", "/dev/ttyACM*", "/dev/ttyAMA*"]:
            for path in glob.glob(pattern):
                ports.append({
                    "device": path,
                    "description": "Standard USB/Serial CDC Interface",
                    "hwid": "Direct /dev enumeration"
                })
        return ports, None
    elif sys.platform == "darwin":
        for path in glob.glob("/dev/cu.*"):
            ports.append({
                "device": path,
                "description": "macOS Serial Port",
                "hwid": "Direct /dev enumeration"
            })
        return ports, None

    return [], "pySerial not installed. Run 'pip install pyserial' for comprehensive hardware scanning."


class UARTConsole:
    """Manages serial capture, live timestamped logging, and hex/text representation."""

    def __init__(
        self,
        port: str,
        baud: int = 115200,
        data_bits: int = 8,
        parity: str = "N",
        stop_bits: float = 1,
        timeout: float = 0.5,
        mock_mode: bool = False
    ):
        self.port = port
        self.baud = baud
        self.data_bits = data_bits
        self.parity = parity
        self.stop_bits = stop_bits
        self.timeout = timeout
        self.mock_mode = mock_mode
        self.connection: Any = None
        self.is_connected = False
        self.bytes_received = 0

    def connect(self) -> Tuple[bool, str]:
        """Establishes connection to serial device or mock backend."""
        if self.mock_mode or self.port.startswith("MOCK"):
            self.connection = MockSerialBackend(port=self.port, baudrate=self.baud)
            self.is_connected = True
            return True, f"Connected to Mock UART Backend on {self.port} at {self.baud} baud (Simulated)."

        if not _HAS_PYSERIAL:
            return False, "pySerial is not installed. Install with 'pip install pyserial' or use mock mode."

        try:
            parity_map = {
                "N": serial.PARITY_NONE,
                "E": serial.PARITY_EVEN,
                "O": serial.PARITY_ODD,
            }
            stop_map = {
                1: serial.STOPBITS_ONE,
                1.5: serial.STOPBITS_ONE_POINT_FIVE,
                2: serial.STOPBITS_TWO,
            }

            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                bytesize=self.data_bits,
                parity=parity_map.get(self.parity, serial.PARITY_NONE),
                stopbits=stop_map.get(self.stop_bits, serial.STOPBITS_ONE),
                timeout=self.timeout
            )
            self.is_connected = True
            return True, f"Hardware serial port '{self.port}' opened at {self.baud} baud (8N1, read-only)."
        except Exception as e:
            self.is_connected = False
            return False, f"Failed to open port '{self.port}': {e}"

    def close(self) -> None:
        """Closes serial connection safely."""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None
        self.is_connected = False

    def stream_and_log(
        self,
        output_file: Optional[Path] = None,
        max_duration_sec: Optional[float] = None,
        max_bytes: Optional[int] = None,
        display: bool = True
    ) -> Dict[str, Any]:
        """Reads incoming bytes, formats with timestamp, and writes to log."""
        if not self.is_connected:
            raise RuntimeError("Cannot stream: serial port is not connected.")

        start_time = time.time()
        log_fh = output_file.open("a", encoding="utf-8") if output_file else None

        if display:
            print(HARDWARE_SAFETY_NOTICE)
            print(f"{styler.badge('INFO')} Listening on {self.port} ({self.baud} baud). Press Ctrl+C to exit.\n")

        collected_lines = []
        raw_buffer = bytearray()

        try:
            while True:
                if max_duration_sec and (time.time() - start_time) > max_duration_sec:
                    break
                if max_bytes and self.bytes_received >= max_bytes:
                    break

                try:
                    chunk = self.connection.read(128)
                except Exception as e:
                    if display:
                        print(f"\n{styler.badge('FAIL')} Read error / connection lost: {e}")
                    break

                if chunk:
                    self.bytes_received += len(chunk)
                    raw_buffer.extend(chunk)

                    # Split completed lines
                    while b"\n" in raw_buffer:
                        line_bytes, raw_buffer = raw_buffer.split(b"\n", 1)
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        text = line_bytes.decode("utf-8", errors="replace").rstrip("\r")
                        hex_repr = " ".join(f"{b:02X}" for b in line_bytes[:16])

                        entry = f"[{now_str}] {text}"
                        collected_lines.append(entry)

                        if log_fh:
                            log_fh.write(entry + "\n")
                            log_fh.flush()

                        if display:
                            print(f"{styler.DIM}[{now_str}]{styler.RESET} {text}")
                else:
                    time.sleep(0.01)

        except KeyboardInterrupt:
            if display:
                print(f"\n{styler.badge('INFO')} Monitoring stopped by user (Ctrl+C).")
        finally:
            if log_fh:
                log_fh.close()

        duration = time.time() - start_time
        return {
            "port": self.port,
            "baud": self.baud,
            "bytes_received": self.bytes_received,
            "lines_captured": len(collected_lines),
            "duration_sec": round(duration, 3),
            "output_file": str(output_file) if output_file else None,
            "sample_lines": collected_lines[:20]
        }
