"""Forensic and diagnostic report generator (JSON, TXT, Markdown)."""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List

from rbrt import __version__, TOOLKIT_NAME
from rbrt.config import get_config

@dataclass
class ReportMetadata:
    toolkit: str
    version: str
    operation: str
    started_at: str
    completed_at: str
    success: bool
    input_files: List[Dict[str, Any]]
    parser_info: str
    findings_count: int
    warnings: List[str]
    unsupported_features_noted: List[str]
    error_message: Optional[str] = None

class ReportGenerator:
    """Creates timestamped non-destructive forensic reports in JSON, TXT, and Markdown."""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.started_at = datetime.now().isoformat()
        self.input_files: List[Dict[str, Any]] = []
        self.warnings: List[str] = []
        self.unsupported_notes: List[str] = []
        self.details: Dict[str, Any] = {}
        self.success = True
        self.error_message: Optional[str] = None
        self.parser_info = f"RBRT Engine v{__version__}"

    def add_input_file(self, path: Path, sha256: Optional[str] = None, size: Optional[int] = None) -> None:
        p = Path(path)
        actual_size = size if size is not None else (p.stat().st_size if p.exists() else 0)
        self.input_files.append({
            "path": str(p.resolve()),
            "name": p.name,
            "size_bytes": actual_size,
            "sha256": sha256 or "N/A"
        })

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def add_unsupported_note(self, note: str) -> None:
        self.unsupported_notes.append(note)

    def set_error(self, err: str) -> None:
        self.success = False
        self.error_message = err

    def save(
        self,
        output_format: str = "json",
        custom_destination: Optional[Path] = None,
        overwrite: bool = False
    ) -> Path:
        completed_at = datetime.now().isoformat()
        cfg = get_config()
        cfg.reports_dir.mkdir(parents=True, exist_ok=True)

        fmt = output_format.lower()
        if custom_destination:
            target = custom_destination
        else:
            time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
            target = cfg.reports_dir / f"rbrt_{self.operation_name}_{time_tag}.{fmt}"

        if target.exists() and not overwrite:
            # Prevent accidental file overwrite by appending deduplication index
            stem = target.stem
            suffix = target.suffix
            parent = target.parent
            idx = 1
            while target.exists():
                target = parent / f"{stem}_{idx}{suffix}"
                idx += 1

        meta = ReportMetadata(
            toolkit=TOOLKIT_NAME,
            version=__version__,
            operation=self.operation_name,
            started_at=self.started_at,
            completed_at=completed_at,
            success=self.success,
            input_files=self.input_files,
            parser_info=self.parser_info,
            findings_count=len(self.details),
            warnings=self.warnings,
            unsupported_features_noted=self.unsupported_notes,
            error_message=self.error_message
        )

        if fmt == "json":
            payload = {
                "metadata": asdict(meta),
                "data": self.details
            }
            target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        elif fmt in ("md", "markdown"):
            md_text = self._render_markdown(meta)
            target.write_text(md_text, encoding="utf-8")
        else:  # text
            txt_text = self._render_text(meta)
            target.write_text(txt_text, encoding="utf-8")

        return target

    def _render_text(self, meta: ReportMetadata) -> str:
        lines = [
            f"============================================================",
            f" {TOOLKIT_NAME} (v{__version__}) - Operation Report",
            f"============================================================",
            f"Operation:         {meta.operation}",
            f"Started:           {meta.started_at}",
            f"Completed:         {meta.completed_at}",
            f"Status:            {'SUCCESS' if meta.success else 'FAILURE'}",
            f"Engine:            {meta.parser_info}",
            f"------------------------------------------------------------",
            f"INPUT FILES:",
        ]
        for f in meta.input_files:
            lines.append(f"  • {f['name']} ({f['size_bytes']:,} bytes)")
            lines.append(f"    SHA-256: {f['sha256']}")

        if meta.warnings:
            lines.append(f"------------------------------------------------------------")
            lines.append(f"WARNINGS ({len(meta.warnings)}):")
            for w in meta.warnings:
                lines.append(f"  [!] {w}")

        if meta.unsupported_features_noted:
            lines.append(f"------------------------------------------------------------")
            lines.append(f"UNSUPPORTED / RESPONSIBLE USAGE NOTES:")
            for u in meta.unsupported_features_noted:
                lines.append(f"  [-] {u}")

        if meta.error_message:
            lines.append(f"------------------------------------------------------------")
            lines.append(f"ERROR: {meta.error_message}")

        lines.append(f"============================================================")
        return "\n".join(lines)

    def _render_markdown(self, meta: ReportMetadata) -> str:
        lines = [
            f"# {TOOLKIT_NAME} Report: {meta.operation}",
            f"",
            f"- **Version**: `v{__version__}`",
            f"- **Execution Status**: `{'SUCCESS' if meta.success else 'FAILED'}`",
            f"- **Timestamp**: `{meta.completed_at}`",
            f"- **Engine**: `{meta.parser_info}`",
            f"",
            f"## Input Files",
            f"",
            f"| Filename | Size (Bytes) | SHA-256 |",
            f"| :--- | :--- | :--- |",
        ]
        for f in meta.input_files:
            lines.append(f"| `{f['name']}` | {f['size_bytes']:,} | `{f['sha256']}` |")

        if meta.warnings:
            lines.append(f"\n## Warnings")
            for w in meta.warnings:
                lines.append(f"- :warning: {w}")

        if meta.unsupported_features_noted:
            lines.append(f"\n## Operational Constraints")
            for u in meta.unsupported_features_noted:
                lines.append(f"- :information_source: {u}")

        return "\n".join(lines)


def list_existing_reports() -> List[Dict[str, Any]]:
    """Lists generated reports in the configured reports directory."""
    cfg = get_config()
    if not cfg.reports_dir.exists():
        return []
    reports = []
    for f in sorted(cfg.reports_dir.glob("rbrt_*"), key=lambda p: p.stat().st_mtime, reverse=True):
        reports.append({
            "name": f.name,
            "path": str(f.resolve()),
            "size": f.stat().st_size,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })
    return reports
