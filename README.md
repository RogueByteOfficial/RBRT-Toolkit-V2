# RogueByte RBRT Toolkit V2

> **Cross-platform PS4/PS5 hardware diagnostics, UART serial console logging, firmware inspection, binary comparison, and ELF analysis toolkit.**

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20WSL2%20%7C%20Windows-brightgreen.svg)](#supported-operating-environments)
[![Tests](https://img.shields.io/badge/tests-39%20passed-success.svg)](tests/)

---

## 1. Project Overview and Goals

**RogueByte RBRT Toolkit V2** (`rbrt`) is a modular, production-grade command-line forensic and hardware diagnostics platform designed for authorized repair engineers, embedded systems technicians, firmware analysts, and digital forensics specialists.

Unlike tools that rely on unverified claims or cloud APIs, **RBRT Toolkit V2** is completely self-contained, operates 100% offline, and enforces non-destructive analysis principles. It provides rigorous local environment health checks (`rbrt doctor`), safe UART serial console logging with hardware safety protections, high-performance streaming chunked binary file comparison, pure-Python 32/64-bit ELF analysis, PlayStation Update Package (`SCE\0`) container inspection, user-supplied dump cataloging, and automated forensic report generation in JSON, TXT, and Markdown formats.

### Developer & Official Links
- **Organization**: RogueByte
- **GitHub**: [github.com/RogueByteOfficial/RBRT-Toolkit-V2](https://github.com/RogueByteOfficial/RBRT-Toolkit-V2)
- **Official Website**: [https://roguebyte.online](https://roguebyte.online)
- **Ko-fi Sponsorship**: [https://ko-fi.com/roguebyte](https://ko-fi.com/roguebyte)
- **Security & Inquiries**: `contact@roguebyte.online`
- **Marketing Manager** : Adel Mouahdi (عادل مواحذي)
- **Contacts** : contact@roguebyte.online.com

---

## 2. Feature Matrix & Implementation Status

| Subsystem / Feature | Capability | Implementation Status | Test Status | Operational Notes |
| :--- | :--- | :---: | :---: | :--- |
| **RBRT Doctor** | Environment audit, OS, kernel, arch, venv, disk, tools | **Implemented** | **Tested (Pass)** | No false failures for missing optional tools |
| **Device Info** | Host specs, distro, endianness, bitness | **Implemented** | **Tested (Pass)** | Real system data, never fabricated |
| **Interactive UI** | [1]-[10] numbered interactive terminal menu | **Implemented** | **Tested (Pass)** | Rich styling with pure ANSI fallback |
| **UART Enumeration**| Serial port discovery (pySerial + /dev/tty scan) | **Implemented** | **Tested (Pass)** | Graceful when no devices are plugged in |
| **UART Logging** | Safe timestamped logging, hex + ASCII display | **Implemented** | **Tested (Pass)** | Read-only mode default; 1.8V/3.3V voltage warnings |
| **Mock Serial** | Simulated Southbridge / Syscon UART stream | **Implemented** | **Tested (Pass)** | Enables 100% offline testing without hardware |
| **BIN Inspection** | Size, chunked SHA-256, format hints, entropy | **Implemented** | **Tested (Pass)** | Detects unprogrammed 0xFF / blank 0x00 flash |
| **BIN Diffing** | Streaming chunk diff, offset, delta, context | **Implemented** | **Tested (Pass)** | Never loads multi-GB files completely into RAM |
| **ELF Analyzer** | ELF32/64 header, segments, sections, symbols | **Implemented** | **Tested (Pass)** | Pure Python struct parser + pyelftools support |
| **ELF Diffing** | Section-level delta, entry point, architecture | **Implemented** | **Tested (Pass)** | Identifies modified, added, removed sections |
| **PUP Inspector** | SCE\0 container header, versions, entry table | **Implemented** | **Tested (Pass)** | Transparently reports encrypted payload status |
| **PUP Decryption** | Direct proprietary cryptographic key extraction | **Unsupported** | **Excluded** | Intentional: RBRT does not bundle proprietary keys |
| **Dump Manager** | User dump cataloging, metadata, comparison | **Implemented** | **Tested (Pass)** | Non-destructive; preserves source files |
| **Log Analyzer** | Diagnostic log anomaly detection, Syscon codes | **Implemented** | **Tested (Pass)** | Community mapping hints; transparent regex |
| **Reporting** | JSON, TXT, and Markdown report export | **Implemented** | **Tested (Pass)** | Timestamped, reproducible, audit-ready |

---

## 3. Supported Operating Environments

- **Primary Targets**:
  - Ubuntu Linux (20.04 LTS, 22.04 LTS, 24.04 LTS)
  - Debian GNU/Linux (11 Bullseye, 12 Bookworm)
  - Kali Linux (Rolling)
  - WSL2 (Windows Subsystem for Linux running Ubuntu or Debian)
- **Secondary Targets**:
  - Windows 10/11 (Python 3.10+ in PowerShell / Command Prompt with pySerial COM ports)
  - macOS (Monterey, Ventura, Sonoma)
- **Termux (Android)**: Experimental (Core file inspection, ELF analysis, and BIN diffing work offline via `python3`; physical UART requires OTG USB-serial permissions).

---

## 4. Quick Installation

```bash
# 1. Update system package index and install prerequisites
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

# 2. Clone repository (replace with your repository URL)
git clone https://github.com/RogueByteOfficial/RBRT-Toolkit-V2.git RBRT-Toolkit-V2
cd RBRT-Toolkit-V2

# 3. Create and activate a clean Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Upgrade pip and install RBRT in editable mode
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

# 5. Verify installation
rbrt --help
rbrt doctor

# 6. Execute automated test suite
python tests/run_tests.py
```

---

## 5. CLI Commands Quick Reference

```bash
# Launch interactive terminal interface
rbrt

# Run environment health check
rbrt doctor
rbrt doctor --json
rbrt doctor --report reports/doctor_audit.json

# Host system and runtime inspection
rbrt device

# UART serial console operations
rbrt uart ports
rbrt uart connect --port /dev/ttyUSB0 --baud 115200
rbrt uart log --port /dev/ttyUSB0 --baud 115200 --output logs/console_boot.log
# Hardware-free mock testing
rbrt uart log --port MOCK --baud 115200 --output logs/mock_test.log --mock --duration 1.0

# Binary file analysis and comparison
rbrt bin inspect firmware.bin
rbrt bin compare original.bin modified.bin

# ELF executable analysis
rbrt elf analyze extracted_kernel.elf
rbrt elf compare stock.elf patched.elf

# PlayStation PUP firmware inspection
rbrt pup inspect PS4UPDATE.PUP
rbrt pup compare update_v1.pup update_v2.pup

# Flash dump manager
rbrt dump inspect flash_dump.bin --model CUH-1215A --board SAC-001

# Report history
rbrt report list
rbrt report export --format json
```

---

## 6. Hardware Voltage & Console Safety Notice

> **CRITICAL WARNING FOR EMBEDDED & CONSOLE HARDWARE (PS4 / PS5 / SYSCON / SOUTHBRIDGE):**
> - Standard PC serial ports and older USB adapters operate at **5V TTL logic**.
> - Modern gaming console diagnostic test points (such as Southbridge UART and Syscon test pins) operate at **1.8V or 3.3V logic levels**.
> - **NEVER connect a 5V TX/RX line directly to 1.8V/3.3V console test points.** Direct 5V exposure will permanently burn out the Southbridge or Syscon controller.
> - Always utilize an isolated 3.3V/1.8V compatible USB-UART adapter (e.g., FTDI FT232R with voltage jumper set to 3.3V or level-shifted CP2102).
> - Verify common chassis ground before powering the host PC or target console.
> - Default to read-only capture. Never transmit random serial characters to diagnostic ports without knowing the protocol specification.

---

## 7. License & Credits

Released under the **MIT License**. See [LICENSE](LICENSE) for details.  
Built by **RogueByte** ([https://roguebyte.online](https://roguebyte.online)).
Support open-source forensics: [Ko-fi](https://ko-fi.com/roguebyte).
