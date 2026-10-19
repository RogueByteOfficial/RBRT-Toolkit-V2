# Binary Analysis & Chunked Diffing Guide — RogueByte RBRT Toolkit V2

## 1. Non-Destructive Binary Inspection

The `rbrt bin inspect` command performs deep static analysis on raw firmware, BIOS, and flash dumps:

```bash
rbrt bin inspect original_dump.bin
```

### Metrics Evaluated
- **Exact File Size**: Number of bytes and human-readable scale.
- **Cryptographic Digest**: Full-file SHA-256 computed in 64 KB streaming chunks.
- **Format Signatures**: Recognition of ELF, SCE containers, Gzip, XZ, PNG, PDF, and zeroed flash regions.
- **Shannon Entropy**: Measures randomness on a scale from 0.0 to 8.0 bits per byte.
  - Low entropy (0.0 – 2.0): Blank regions, repetitive padding, uninitialized flash.
  - Medium entropy (3.0 – 6.0): Uncompressed code (`.text` segments, raw data).
  - High entropy (7.2 – 8.0): Compressed or encrypted firmware blocks.
- **Filler Pattern Analysis**: Automatic detection of factory unprogrammed NOR flash (`0xFF` padding) or cleared memory (`0x00`).

---

## 2. Streaming Chunk Comparison (`rbrt bin compare`)

When comparing two multi-gigabyte firmware images, traditional tools often exhaust available RAM by loading both files into memory.

**RBRT Toolkit V2 solves this:**
- Streams both files synchronously in fixed 64 KB buffers.
- Consumes $< 30\text{ MB}$ of memory regardless of whether files are 10 MB or 100 GB.
- Identifies the exact first divergence offset.
- Tallies total byte differences and delta percentage.
- Automatically handles files of unequal length.
- Outputs side-by-side hex context around divergences.

```bash
rbrt bin compare dump_rev1.bin dump_rev2.bin
```
