# Quickstart Guide — RogueByte RBRT Toolkit V2

Get started with RogueByte RBRT Toolkit V2 in under 2 minutes.

---

## 1. Launching the Interactive Terminal Menu

If you prefer a guided terminal workflow, simply execute:

```bash
rbrt
```

You will be presented with the RogueByte startup banner and numbered menu:

```
╔════════════════════════════════════════════════════════════════════════╗
║                            ROGUEBYTE                                   ║
║                        RBRT TOOLKIT V2                                 ║
║         Hardware Diagnostics | Firmware Analysis | Digital Forensics   ║
╚════════════════════════════════════════════════════════════════════════╝

 [1]  RBRT Doctor (Environment Diagnostics)
 [2]  Device & Environment Information
 [3]  UART Serial Console
 [4]  Console Diagnostic Logs
 [5]  BIN Analyzer & Comparator
 [6]  PUP Firmware Inspector
 [7]  ELF Analyzer
 [8]  Dump Manager
 [9]  Reports & Session History
 [10] Settings & Dependency Status
 [0]  Exit
```

---

## 2. Common CLI Workflows

### 1. Diagnose Environment
```bash
rbrt doctor
```

### 2. Inspect a Binary File (Flash / Firmware)
```bash
rbrt bin inspect samples/flash_dump.bin
```
Provides:
- Exact file size and humanized notation
- Streaming SHA-256 cryptographic digest
- File format magic signature detection
- Shannon entropy estimation (detecting encrypted vs. plain vs. compressed regions)
- Detection of unprogrammed/blank flash filler bytes (predominant `0xFF` or `0x00`)
- Hexadecimal offset preview of the first 128 bytes

### 3. Compare Two Firmware Dumps
```bash
rbrt bin compare original_bios.bin updated_bios.bin
```
Streams both files in 64 KB chunks, reporting:
- Divergence status and byte count
- Exact percentage of differences
- First byte offset where mismatch begins
- Side-by-side hex context preview around divergences

### 4. Analyze an ELF Binary
```bash
rbrt elf analyze kernel.elf
```
Inspects 32/64-bit ELF headers, architecture (x86-64, ARM, AArch64, MIPS, etc.), entry points, segments (`PT_LOAD`), sections (`.text`, `.rodata`), dynamic libraries, and symbol tables.

### 5. Listen to Serial Console Logs (UART)
```bash
# Check connected USB-serial adapters:
rbrt uart ports

# Start read-only capture with timestamps:
rbrt uart log --port /dev/ttyUSB0 --baud 115200 --output boot_capture.log
```

---

## Developer Support
Website: [https://roguebyte.online](https://roguebyte.online)  
Contact: `contact@roguebyte.online`
