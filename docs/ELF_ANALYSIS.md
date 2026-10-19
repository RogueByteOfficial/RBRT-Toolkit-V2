# ELF Analysis & Difference Engine — RogueByte RBRT Toolkit V2

## 1. Pure-Python & Pyelftools Hybrid Engine

The ELF analyzer in RBRT Toolkit V2 implements a complete pure-Python `struct` parser for 32-bit and 64-bit ELF binaries. If `pyelftools` is installed in the Python environment, the toolkit seamlessly enhances analysis with DWARF and dynamic library tag extraction (`DT_NEEDED`).

### Supported Architecture Identification
- `x86-64` (AMD64 / Intel 64)
- `x86` (Intel 80386)
- `AArch64` (ARM 64-bit)
- `ARM` (32-bit)
- `MIPS`
- `PowerPC`
- `SPARC`
- `RISC-V`

---

## 2. Command Examples

```bash
# Detailed static analysis
rbrt elf analyze /path/to/extracted.elf

# Section-level comparison between two binaries
rbrt elf compare stock_kernel.elf patched_kernel.elf
```

### ELF Comparison Output
- Architecture match / mismatch
- Entry point match / divergence
- Count of identical, modified, added, and removed sections
- Section address, offset, and size deltas
