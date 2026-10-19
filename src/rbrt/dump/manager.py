"""User-supplied hardware and firmware dump manager.
Provides cataloging, integrity verification, repeated-byte filler detection, and non-destructive analysis.
"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional

from rbrt.utils.hashing import compute_file_sha256
from rbrt.bin_tools.analyzer import inspect_binary_file, compare_binary_files
from rbrt.config import get_config

@dataclass
class DumpRecord:
    dump_id: str
    file_path: str
    file_name: str
    size_bytes: int
    sha256: str
    imported_at: str
    device_model: Optional[str]
    board_revision: Optional[str]
    source_notes: Optional[str]
    entropy_estimate: float
    is_repetitive: bool
    repetitive_byte: Optional[int]


class DumpManager:
    """Manages dump catalogs and non-destructive verification."""

    def __init__(self, manifest_path: Optional[Path] = None):
        cfg = get_config()
        self.manifest_file = manifest_path or (cfg.workspace_dir / "dump_manifest.json")
        self.records: Dict[str, DumpRecord] = {}
        self._load_manifest()

    def _load_manifest(self) -> None:
        if self.manifest_file.exists():
            try:
                data = json.loads(self.manifest_file.read_text(encoding="utf-8"))
                for item in data.get("dumps", []):
                    rec = DumpRecord(**item)
                    self.records[rec.dump_id] = rec
            except Exception:
                pass

    def save_manifest(self) -> None:
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "2.0.0",
            "updated_at": datetime.now().isoformat(),
            "dumps": [asdict(r) for r in self.records.values()]
        }
        self.manifest_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def register_dump(
        self,
        file_path: Path,
        device_model: Optional[str] = None,
        board_revision: Optional[str] = None,
        source_notes: Optional[str] = None
    ) -> DumpRecord:
        """Inspects and registers an existing user-supplied dump non-destructively."""
        if not file_path.exists():
            raise FileNotFoundError(f"Dump file does not exist: {file_path}")

        inspection = inspect_binary_file(file_path)
        dump_id = f"dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_path.stem[:12]}"

        record = DumpRecord(
            dump_id=dump_id,
            file_path=str(file_path.resolve()),
            file_name=file_path.name,
            size_bytes=inspection.size_bytes,
            sha256=inspection.sha256,
            imported_at=datetime.now().isoformat(),
            device_model=device_model,
            board_revision=board_revision,
            source_notes=source_notes,
            entropy_estimate=inspection.entropy_estimate,
            is_repetitive=inspection.is_repetitive,
            repetitive_byte=inspection.repetitive_byte
        )

        self.records[dump_id] = record
        self.save_manifest()
        return record

    def list_dumps(self) -> List[DumpRecord]:
        return list(self.records.values())

    def compare_dumps(self, dump_id_a: str, dump_id_b: str) -> Dict[str, Any]:
        """Compares two registered dumps."""
        if dump_id_a not in self.records:
            raise KeyError(f"Dump ID '{dump_id_a}' not found in manifest.")
        if dump_id_b not in self.records:
            raise KeyError(f"Dump ID '{dump_id_b}' not found in manifest.")

        ra = self.records[dump_id_a]
        rb = self.records[dump_id_b]

        bin_result = compare_binary_files(Path(ra.file_path), Path(rb.file_path))
        return {
            "dump_a": asdict(ra),
            "dump_b": asdict(rb),
            "comparison": asdict(bin_result)
        }
