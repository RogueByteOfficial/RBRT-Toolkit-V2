# Automated Testing Guide — RogueByte RBRT Toolkit V2

## Test Suite Design

The test suite in RBRT Toolkit V2 provides 100% offline, hermetic testing of all CLI commands, forensic parsers, chunked binary comparisons, error code analyzers, and UART mocking.

No physical hardware, serial adapters, or retail consoles are required.

---

## Running the Automated Test Suite

### Via Integrated Test Runner:
```bash
python tests/run_tests.py
```

### Via Standard Library Unittest:
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

### Via Pytest (if installed):
```bash
pytest -v
```

---

## What is Tested
1. **CLI Commands**: `--help`, `--version`, `doctor`, `device`, `uart ports`, `uart log (mock)`, `bin inspect`, `bin compare`, `elf analyze`, `elf compare`, `pup inspect`, `pup compare`, `dump inspect`, `report list`, `report export`.
2. **Binary Analyzer**: Empty files, large 128KB chunked files, repeated 0xFF blank flash detection, SHA-256 accuracy, side-by-side context diffing.
3. **ELF Parser**: Minimal valid ELF64, truncated ELF, non-ELF files, section difference calculator.
4. **PUP Inspector**: SCE\0 magic validation, big-endian header unpacking, entry table bounds, invalid files.
5. **UART Engine**: Mock serial backend read/write, safe streaming, timestamp formatting, file writing, graceful disconnect.
6. **Diagnostic Logs**: Syscon error code parsing, regex matching, message deduplication and ranking.
7. **Reports**: JSON schema validation, Markdown formatting, TXT rendering, non-destructive file collision handling.
