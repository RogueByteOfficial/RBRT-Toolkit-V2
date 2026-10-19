"""Generates synthetic test fixtures for binary, ELF, PUP, UART, and logs testing."""

import struct
from pathlib import Path
from typing import Dict

def create_synthetic_fixtures(fixtures_dir: Path) -> Dict[str, Path]:
    """Generates small, large, malformed, and synthetic fixtures safely in temporary/target directory."""
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    paths: Dict[str, Path] = {}

    # 1. Empty file
    empty_file = fixtures_dir / "sample_empty.bin"
    empty_file.write_bytes(b"")
    paths["empty"] = empty_file

    # 2. Valid minimal ELF64 binary (x86_64, little-endian, ET_EXEC)
    elf64_file = fixtures_dir / "sample_valid_x86_64.elf"
    # Header: \x7fELF, 2 (64-bit), 1 (LE), 1 (ver), 0 (sysv), 0 pad (8 bytes)
    e_ident = b"\x7fELF\x02\x01\x01\x00" + (b"\x00" * 8)
    # e_type=2 (ET_EXEC), e_machine=0x3e (x86-64), e_version=1, e_entry=0x400000,
    # e_phoff=64, e_shoff=128, e_flags=0, e_ehsize=64, e_phentsize=56, e_phnum=1,
    # e_shentsize=64, e_shnum=2, e_shstrndx=1
    elf_hdr = struct.pack("<16sHHIQQQIHHHHHH",
        e_ident, 2, 0x3E, 1, 0x400000, 64, 128, 0, 64, 56, 1, 64, 2, 1
    )
    # 1 dummy Program Header (56 bytes): PT_LOAD=1, flags=5 (RX), offset=0, vaddr=0x400000, paddr=0x400000, filesz=0x200, memsz=0x200, align=0x1000
    ph = struct.pack("<IIQQQQQQ", 1, 5, 0, 0x400000, 0x400000, 0x200, 0x200, 0x1000)
    # Fill up to offset 128
    pad = b"\x90" * (128 - (len(elf_hdr) + len(ph)))
    # Section Header 0: NULL (64 bytes)
    sh0 = b"\x00" * 64
    # Section Header 1: .shstrtab SHT_STRTAB (type=3), flags=0, addr=0, offset=256, size=16
    sh1 = struct.pack("<IIQQQQIIQQ", 1, 3, 0, 0, 256, 16, 0, 0, 1, 0)
    # Shstrtab content at 256
    pad2 = b"\x00" * (256 - (128 + len(sh0) + len(sh1)))
    shstrtab = b"\x00.shstrtab\x00\x00\x00\x00\x00\x00"

    elf_bytes = elf_hdr + ph + pad + sh0 + sh1 + pad2 + shstrtab
    elf64_file.write_bytes(elf_bytes)
    paths["valid_elf"] = elf64_file

    # 3. Corrupted / truncated ELF
    corrupt_elf = fixtures_dir / "sample_truncated.elf"
    corrupt_elf.write_bytes(b"\x7fELF\x02\x01\x01\x00truncated")
    paths["corrupt_elf"] = corrupt_elf

    # 4. Repetitive filler binary (simulating blank unprogrammed 0xFF flash)
    repetitive_bin = fixtures_dir / "sample_blank_flash.bin"
    repetitive_bin.write_bytes(b"\xff" * 4096)
    paths["repetitive"] = repetitive_bin

    # 5. Normal binary A and modified binary B
    bin_a = fixtures_dir / "firmware_a.bin"
    data_a = bytes(range(256)) * 4  # 1024 bytes
    bin_a.write_bytes(data_a)
    paths["bin_a"] = bin_a

    bin_b = fixtures_dir / "firmware_b.bin"
    data_b = bytearray(data_a)
    data_b[100] = 0xAA  # Divergence
    data_b[101] = 0xBB
    bin_b.write_bytes(data_b)
    paths["bin_b"] = bin_b

    # 6. Large chunked comparison file (128 KB)
    large_bin_a = fixtures_dir / "large_chunk_a.bin"
    large_bin_b = fixtures_dir / "large_chunk_b.bin"
    chunk_pattern = b"RogueByteForensicsTestDataChunk64KB!" * 1800  # ~64KB
    large_bin_a.write_bytes(chunk_pattern * 2)  # ~128KB
    large_bin_b.write_bytes(chunk_pattern + (b"\x00" * 64) + chunk_pattern[64:])
    paths["large_a"] = large_bin_a
    paths["large_b"] = large_bin_b

    # 7. Unsupported / Valid-Header PUP container
    pup_file = fixtures_dir / "sample_package.pup"
    # SCE\0 container header (Big-endian)
    # 4s magic, pkg_type=1, img_ver=0x00010000, flags=0, entry_count=1, hdr_len=72, pkg_len=128
    pup_hdr = struct.pack(">4sIIIQQQ", b"SCE\x00", 1, 0x00010000, 0, 1, 72, 128)
    # Entry 0 (32 bytes): id=1, offset=72, size=56, flags=1 (encrypted)
    pup_entry = struct.pack(">QQQQ", 1, 72, 56, 1)
    pup_payload = b"\xca\xfe\xba\xbe" * 14  # Simulated encrypted payload
    pup_file.write_bytes(pup_hdr + pup_entry + pup_payload)
    paths["pup"] = pup_file

    # 8. Sample UART / Syscon console log
    log_file = fixtures_dir / "sample_syscon.log"
    log_content = (
        "[2026-10-19 12:00:00.001] SBOOT: Cold boot sequence initiated\n"
        "[2026-10-19 12:00:00.015] SYSCON: Power rail OK (80801000)\n"
        "[2026-10-19 12:00:00.080] WARNING: Thermal prober offset warning detected\n"
        "[2026-10-19 12:00:00.120] ERR: SYSCON FAULT 80801500\n"
        "[2026-10-19 12:00:00.200] Repeated event message\n"
        "[2026-10-19 12:00:00.201] Repeated event message\n"
        "[2026-10-19 12:00:00.202] Repeated event message\n"
        "[2026-10-19 12:00:00.300] KERNEL: PANIC_KERNEL trapped at 0xFFFFFF8000100000\n"
    )
    log_file.write_text(log_content, encoding="utf-8")
    paths["log"] = log_file

    return paths
