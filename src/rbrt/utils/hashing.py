"""Hashing utilities with streaming chunk support for arbitrary file sizes."""

import hashlib
from pathlib import Path
from typing import Dict, Union

CHUNK_SIZE = 65536  # 64 KB

def compute_file_sha256(file_path: Union[str, Path]) -> str:
    """Computes SHA-256 hash in 64KB streaming chunks to handle multi-gigabyte dumps."""
    hasher = hashlib.sha256()
    path = Path(file_path)
    with path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def compute_file_hashes(file_path: Union[str, Path]) -> Dict[str, str]:
    """Computes SHA-256 and MD5 simultaneously in streaming chunks."""
    h_sha256 = hashlib.sha256()
    h_md5 = hashlib.md5()
    path = Path(file_path)
    with path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            h_sha256.update(chunk)
            h_md5.update(chunk)
    return {
        "sha256": h_sha256.hexdigest(),
        "md5": h_md5.hexdigest(),
    }
