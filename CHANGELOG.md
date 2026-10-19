# Changelog

All notable changes to the RogueByte RBRT Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-10-19

### Added
- Complete rewrite of RBRT Toolkit into modular, cross-platform architecture.
- Core CLI command `rbrt` with subcommands: `doctor`, `device`, `uart`, `bin`, `elf`, `pup`, `dump`, `report`.
- Interactive terminal user interface with numbered options [1]-[10] and ANSI/Rich styling fallback.
- Local diagnostic module `rbrt doctor` testing Python runtime, venv, disk metrics, toolchain utilities, permissions, and serial discovery.
- Hardware-safe UART serial console manager with read-only default, baud rate control, and mock test backend.
- High-efficiency chunk-based binary comparator supporting multi-gigabyte firmware images with low RAM usage.
- Detection of unprogrammed/blank flash dumps (0xFF / 0x00 filler pattern analysis).
- Pure-Python native 32/64-bit ELF structural parser with section and segment mapping, entry point validation, and symbol estimation.
- Transparent pyelftools integration for dynamic tag and dependency resolution.
- SCE PlayStation Update Package (`PUP`) container inspector with table-of-contents validation and encrypted payload detection.
- Non-destructive Dump Manager cataloging user-provided flash dumps with metadata.
- Console diagnostic text log analyzer with pattern-based anomaly detection and Syscon error code parsing.
- Automated forensic report generator outputting audit-ready JSON, TXT, and Markdown files.
- Automated test suite comprising 39 passing unit and integration tests.
