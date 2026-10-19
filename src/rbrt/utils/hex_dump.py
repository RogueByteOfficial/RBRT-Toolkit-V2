"""Hexadecimal inspection, formatting, and diff context utilities."""

from typing import List, Tuple

def format_hex_preview(data: bytes, base_offset: int = 0, bytes_per_line: int = 16) -> str:
    """Formats bytes into canonical hex + ASCII dump format."""
    lines: List[str] = []
    for i in range(0, len(data), bytes_per_line):
        chunk = data[i:i + bytes_per_line]
        hex_parts: List[str] = []
        ascii_parts: List[str] = []

        for b in chunk:
            hex_parts.append(f"{b:02X}")
            ascii_parts.append(chr(b) if 32 <= b <= 126 else ".")

        # Pad hex part if incomplete line
        hex_str = " ".join(hex_parts).ljust(bytes_per_line * 3 - 1)
        # Split into 8-byte halves for readability
        if len(hex_parts) > 8:
            hex_str = " ".join(hex_parts[:8]) + "  " + " ".join(hex_parts[8:])
            hex_str = hex_str.ljust(bytes_per_line * 3)

        ascii_str = "".join(ascii_parts)
        offset = base_offset + i
        lines.append(f"{offset:08X}:  {hex_str}  |{ascii_str}|")

    return "\n".join(lines)

def format_diff_context(
    data_a: bytes,
    data_b: bytes,
    offset: int,
    context_bytes: int = 16
) -> List[Tuple[str, str, str]]:
    """Formats a side-by-side comparison line around an offset difference."""
    rows: List[Tuple[str, str, str]] = []
    max_len = max(len(data_a), len(data_b))
    for i in range(max_len):
        cur_offset = f"0x{offset + i:08X}"
        byte_a = f"{data_a[i]:02X} ('{chr(data_a[i]) if 32 <= data_a[i] <= 126 else '.'}')" if i < len(data_a) else "<EOF>"
        byte_b = f"{data_b[i]:02X} ('{chr(data_b[i]) if 32 <= data_b[i] <= 126 else '.'}')" if i < len(data_b) else "<EOF>"
        rows.append((cur_offset, byte_a, byte_b))
    return rows
