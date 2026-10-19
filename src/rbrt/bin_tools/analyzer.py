"""Binary file inspection, repeated byte pattern analysis, and chunked comparison engine."""

import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List, Tuple

from rbrt.utils.hashing import compute_file_sha256
from rbrt.utils.hex_dump import format_hex_preview, format_diff_context
from rbrt.utils.styling import styler

CHUNK_SIZE = 65536  # 64 KB chunk size for large file diffing

@dataclass
class BinInspectionResult:
    file_path: str
    file_name: str
    size_bytes: int
    size_human: str
    sha256: str
    format_hint: str
    entropy_estimate: float
    is_repetitive: bool
    repetitive_byte: Optional[int]
    preview_hex: str
    truncation_warning: Optional[str] = None

@dataclass
class BinComparisonResult:
    file_a: str
    file_b: str
    size_a: int
    size_b: int
    sha256_a: str
    sha256_b: str
    identical: bool
    first_diff_offset: Optional[int]
    differing_bytes_count: int
    differing_percentage: float
    size_delta_bytes: int
    context_diffs: List[Dict[str, Any]]
    summary: str


def detect_file_type_hint(header: bytes) -> str:
    """Identifies common file signatures without external dependencies."""
    if header.startswith(b"\x7fELF"):
        return "ELF Executable / Library"
    if header.startswith(b"\x53\x43\x45\x00") or header.startswith(b"SCE\x00"):
        return "PlayStation PUP / SCE Container"
    if header.startswith(b"\x1f\x8b"):
        return "Gzip Compressed Archive"
    if header.startswith(b"PK\x03\x04"):
        return "Zip / JAR / DOCX Archive"
    if header.startswith(b"\x42\x5a\x68"):
        return "Bzip2 Compressed Archive"
    if header.startswith(b"\xfd7zXZ\x00"):
        return "XZ Compressed Archive"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG Image"
    if header.startswith(b"%PDF"):
        return "PDF Document"
    if header.startswith(b"RIFF"):
        return "RIFF Multimedia Container"
    if len(header) >= 4 and header[:4] in (b"\x00\x00\x00\x00", b"\xff\xff\xff\xff"):
        return "Raw Flash / Uninitialized Memory Region"
    return "Generic Binary Data"


def calculate_entropy_and_repetition(file_path: Path) -> Tuple[float, bool, Optional[int]]:
    """Calculates byte distribution, Shannon entropy estimate, and checks for repeated filler patterns (0x00 or 0xFF)."""
    import math

    byte_counts = [0] * 256
    total_bytes = 0
    with file_path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            total_bytes += len(chunk)
            for b in chunk:
                byte_counts[b] += 1

    if total_bytes == 0:
        return 0.0, True, None

    entropy = 0.0
    for count in byte_counts:
        if count > 0:
            p = count / total_bytes
            entropy -= p * math.log2(p)

    # Check if a single byte dominates (>95% of file, e.g. unprogrammed NOR/NAND flash 0xFF or zeroed 0x00)
    for b, count in enumerate(byte_counts):
        if count / total_bytes >= 0.95:
            return round(entropy, 4), True, b

    return round(entropy, 4), False, None


def inspect_binary_file(file_path: Path) -> BinInspectionResult:
    """Performs deep non-destructive analysis on a binary file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Target binary not found: {file_path}")

    size = file_path.stat().st_size
    sha256 = compute_file_sha256(file_path)

    # Read preview header
    with file_path.open("rb") as f:
        header = f.read(512)

    format_hint = detect_file_type_hint(header)
    entropy, is_repetitive, rep_byte = calculate_entropy_and_repetition(file_path)

    trunc_warning = None
    if size == 0:
        trunc_warning = "File is empty (0 bytes)."
    elif is_repetitive:
        b_name = f"0x{rep_byte:02X}" if rep_byte is not None else "None"
        trunc_warning = f"File consists predominantly of repeated byte {b_name} (Possible blank or unprogrammed flash dump)."

    # Format human size
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024 or unit == "GB":
            size_human = f"{size:.2f} {unit}" if unit != "B" else f"{size} B"
            break
        size = size / 1024.0

    preview_hex = format_hex_preview(header[:128])

    return BinInspectionResult(
        file_path=str(file_path.resolve()),
        file_name=file_path.name,
        size_bytes=file_path.stat().st_size,
        size_human=size_human,
        sha256=sha256,
        format_hint=format_hint,
        entropy_estimate=entropy,
        is_repetitive=is_repetitive,
        repetitive_byte=rep_byte,
        preview_hex=preview_hex,
        truncation_warning=trunc_warning,
    )


def compare_binary_files(
    file_a: Path,
    file_b: Path,
    max_context_samples: int = 5
) -> BinComparisonResult:
    """Compares two binary files using chunked streaming.
    Does NOT load entire files into memory, supporting multi-gigabyte files.
    """
    if not file_a.exists():
        raise FileNotFoundError(f"File A not found: {file_a}")
    if not file_b.exists():
        raise FileNotFoundError(f"File B not found: {file_b}")

    size_a = file_a.stat().st_size
    size_b = file_b.stat().st_size
    sha_a = compute_file_sha256(file_a)
    sha_b = compute_file_sha256(file_b)

    if sha_a == sha_b:
        return BinComparisonResult(
            file_a=str(file_a),
            file_b=str(file_b),
            size_a=size_a,
            size_b=size_b,
            sha256_a=sha_a,
            sha256_b=sha_b,
            identical=True,
            first_diff_offset=None,
            differing_bytes_count=0,
            differing_percentage=0.0,
            size_delta_bytes=0,
            context_diffs=[],
            summary="Files are completely identical (100% byte match, identical SHA-256)."
        )

    # Stream both files chunk by chunk
    offset = 0
    first_diff: Optional[int] = None
    diff_count = 0
    context_samples: List[Dict[str, Any]] = []

    with file_a.open("rb") as fa, file_b.open("rb") as fb:
        while True:
            chunk_a = fa.read(CHUNK_SIZE)
            chunk_b = fb.read(CHUNK_SIZE)

            if not chunk_a and not chunk_b:
                break

            min_len = min(len(chunk_a), len(chunk_b))

            # Compare common bytes
            for i in range(min_len):
                if chunk_a[i] != chunk_b[i]:
                    cur_off = offset + i
                    if first_diff is None:
                        first_diff = cur_off
                    diff_count += 1

                    if len(context_samples) < max_context_samples:
                        # Extract surrounding context
                        ctx_start = max(0, i - 4)
                        ctx_end = min(min_len, i + 8)
                        context_samples.append({
                            "offset": f"0x{cur_off:08X}",
                            "byte_a": f"0x{chunk_a[i]:02X}",
                            "byte_b": f"0x{chunk_b[i]:02X}",
                            "context_a": " ".join(f"{b:02X}" for b in chunk_a[ctx_start:ctx_end]),
                            "context_b": " ".join(f"{b:02X}" for b in chunk_b[ctx_start:ctx_end]),
                        })

            # Account for length difference
            if len(chunk_a) != len(chunk_b):
                extra = abs(len(chunk_a) - len(chunk_b))
                diff_count += extra
                if first_diff is None:
                    first_diff = offset + min_len

            offset += max(len(chunk_a), len(chunk_b))

    max_size = max(size_a, size_b)
    diff_pct = (diff_count / max_size * 100.0) if max_size > 0 else 0.0

    summary = (
        f"Files differ: {diff_count:,} byte differences ({diff_pct:.4f}% delta). "
        f"First divergence at offset 0x{first_diff:08X}."
    )
    if size_a != size_b:
        summary += f" Size delta: {abs(size_a - size_b):,} bytes."

    return BinComparisonResult(
        file_a=str(file_a),
        file_b=str(file_b),
        size_a=size_a,
        size_b=size_b,
        sha256_a=sha_a,
        sha256_b=sha_b,
        identical=False,
        first_diff_offset=first_diff,
        differing_bytes_count=diff_count,
        differing_percentage=round(diff_pct, 4),
        size_delta_bytes=abs(size_a - size_b),
        context_diffs=context_samples,
        summary=summary
    )
