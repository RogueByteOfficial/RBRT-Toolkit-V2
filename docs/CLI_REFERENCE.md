# CLI Reference — RogueByte RBRT Toolkit V2

Complete flag reference for all `rbrt` commands and options.

---

## Global Options

- `rbrt -h`, `rbrt --help`: Display overall command documentation.
- `rbrt -v`, `rbrt --version`: Display toolkit version string.

---

## 1. `rbrt doctor`
Inspect local host environment, toolchain binaries, virtual environment, and filesystem permissions.

```bash
rbrt doctor
rbrt doctor --json
rbrt doctor --report <path>
```
- `--json`: Output machine-readable JSON dictionary with audit summary.
- `--report <path>`: Write the resulting JSON assessment directly to `<path>`.

---

## 2. `rbrt device`
Display host system, kernel release, CPU architecture, endianness, bitness, and optional package statuses.

```bash
rbrt device
rbrt device --json
```

---

## 3. `rbrt uart`
Hardware serial console management and logging.

### `rbrt uart ports`
Enumerate detected USB-serial and CDC ACM hardware interfaces.

### `rbrt uart connect`
Open interactive serial session in read-only mode.
- `--port <PORT>`: Serial device name (e.g. `/dev/ttyUSB0`, `COM3`, or `MOCK`).
- `--baud <BAUD>`: Baud rate (default: `115200`).
- `--mock`: Connect to internal simulated UART device.

### `rbrt uart log`
Capture incoming serial stream directly to a timestamped file.
- `--port <PORT>`: Serial device name.
- `--baud <BAUD>`: Baud rate (default: `115200`).
- `--output <FILE>`: Target destination log file.
- `--duration <SEC>`: Stop capture automatically after specified seconds.
- `--mock`: Use internal mock serial stream.

---

## 4. `rbrt bin`
Binary inspection and chunk-based difference comparison.

### `rbrt bin inspect <file>`
- `--json`: Print result as structured JSON.
- `--report <path>`: Export formal audit report.

### `rbrt bin compare <file_a> <file_b>`
- `--json`: Print diff metrics and context in JSON format.
- `--report <path>`: Export formal difference report.

---

## 5. `rbrt elf`
Executable and Linkable Format structural analysis.

### `rbrt elf analyze <file>`
- `--json`: Detailed section, segment, and header fields.
- `--report <path>`: Save analysis report.

### `rbrt elf compare <file_a> <file_b>`
- `--json`: Section size, address, and architecture deltas in JSON.
- `--report <path>`: Save comparison report.

---

## 6. `rbrt pup`
PlayStation Update Package outer container verification.

### `rbrt pup inspect <file>`
- `--json`: Container header, version, and entry table.
- `--report <path>`: Export report.

### `rbrt pup compare <file_a> <file_b>`
- `--json`: Manifest and binary delta.

---

## 7. `rbrt dump`
Manage and catalog user-provided binary flash dumps.

### `rbrt dump inspect <file>`
- `--model <MODEL>`: Hardware model (e.g. `CUH-1215A`, `CFI-1015A`).
- `--board <BOARD>`: Motherboard revision (e.g. `SAC-001`, `EDM-020`).
- `--notes <NOTES>`: Description or acquisition context.
- `--json`: Output dump record as JSON.

---

## 8. `rbrt report`
Audit history management.

### `rbrt report list`
Lists all generated reports in the reports directory.

### `rbrt report export`
- `--format {json,txt,md}`: Target export format.
- `--output <path>`: Target output file.
