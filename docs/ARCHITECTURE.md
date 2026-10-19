# Architecture & Module Design — RogueByte RBRT Toolkit V2

## Architectural Principles

1. **Zero Mandatory Dependencies**: The core functionality of RBRT Toolkit V2 (CLI, Doctor, BIN diffing, ELF parsing, Dump management, reporting) runs strictly on Python standard library modules (`struct`, `hashlib`, `difflib`, `argparse`, `dataclasses`, `pathlib`).
2. **Transparent Acceleration**: Optional packages (`rich`, `pyserial`, `pyelftools`, `pytest`) are dynamically detected. If present, enhanced capabilities are activated; if absent, built-in pure-Python implementations seamlessly take over without crashing.
3. **Streaming Memory Discipline**: No multi-megabyte or multi-gigabyte file is ever read entirely into RAM via `.read()`. All operations stream in 64 KB buffers (`CHUNK_SIZE = 65536`).
4. **Non-Destructive Forensics**: Source binary files, dumps, and input logs are opened strictly in read-only mode (`"rb"`). Reports are saved to a separate configurable directory (`reports/`) with automatic version deduplication.

---

## Directory & Package Layout

```
RBRT-Toolkit-V2/
├── pyproject.toml              # Modern Python packaging configuration (PEP 621)
├── README.md                   # Primary project overview, links, and quickstart
├── LICENSE                     # MIT Open Source License
├── CHANGELOG.md                # Version history and changelog
├── CONTRIBUTING.md             # Developer workflow & PR instructions
├── SECURITY.md                 # Responsible disclosure and security policies
├── Makefile                    # Automation shortcuts (install, test, lint, clean)
├── docs/                       # Comprehensive documentation suite
│   ├── INSTALL.md
│   ├── QUICKSTART.md
│   ├── ARCHITECTURE.md
│   ├── CLI_REFERENCE.md
│   ├── UART_HARDWARE.md
│   ├── BIN_ANALYSIS.md
│   ├── PUP_FORMAT_SUPPORT.md
│   ├── ELF_ANALYSIS.md
│   ├── TROUBLESHOOTING.md
│   ├── TESTING.md
│   └── DEVELOPMENT.md
├── src/
│   └── rbrt/
│       ├── __init__.py         # Package metadata, version, and branding constants
│       ├── main.py             # Console entrypoint
│       ├── cli.py              # Argparse subcommands & command routing
│       ├── config.py           # Paths, workspace settings, safe limits
│       ├── doctor.py           # Environment health diagnostics module
│       ├── device.py           # Host system, architecture, and toolchain inspection
│       ├── terminal_ui.py      # Numbered interactive terminal menu loop
│       ├── uart/
│       │   └── serial_manager.py # pySerial interface, mock serial, safe logging
│       ├── bin_tools/
│       │   └── analyzer.py     # Binary inspector, chunked comparator, entropy
│       ├── elf/
│       │   └── parser.py       # Pure-Python struct ELF32/64 parser + pyelftools
│       ├── pup/
│       │   └── inspector.py    # SCE PUP container inspector & manifest comparator
│       ├── dump/
│       │   └── manager.py      # Dump cataloging, JSON manifest, metadata
│       ├── diagnostics/
│       │   └── log_analyzer.py # Console log parser, regex patterns, Syscon codes
│       ├── reports/
│       │   └── generator.py    # JSON, TXT, and Markdown report builder
│       └── utils/
│           ├── styling.py      # Rich & pure ANSI color styling with badges
│           ├── hashing.py      # Streaming chunked SHA-256 and MD5
│           └── hex_dump.py     # Formatted hex offset and diff context viewer
├── tests/
│   ├── fixtures/
│   │   └── fixture_generator.py # Synthetic non-destructive test generator
│   ├── unit/
│   │   ├── test_doctor.py
│   │   ├── test_bin_tools.py
│   │   ├── test_elf_parser.py
│   │   ├── test_pup.py
│   │   ├── test_uart.py
│   │   ├── test_diagnostics.py
│   │   └── test_reports.py
│   ├── integration/
│   │   └── test_cli.py
│   └── run_tests.py            # Self-contained discovery test runner
└── reports/                    # Default destination for generated audit logs
```
