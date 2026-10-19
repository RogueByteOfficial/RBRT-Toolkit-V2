"""Console diagnostic log parser, timestamp normalizer, and transparent rule-based anomaly detector."""

import re
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple

@dataclass
class DiagnosticMatch:
    rule_name: str
    severity: str  # CRITICAL, ERROR, WARNING, NOTICE, INFO
    line_number: int
    raw_line: str
    normalized_timestamp: Optional[str]
    category: str
    description: str
    code: Optional[str] = None
    context_before: List[str] = None
    context_after: List[str] = None

# Transparent pattern rules for serial and console logs
DEFAULT_PATTERNS = [
    {
        "name": "PANIC_KERNEL",
        "severity": "CRITICAL",
        "category": "Kernel",
        "regex": r"(?:kernel\s+panic|panic:.*|fatal\s+kernel\s+trap)",
        "description": "Kernel panic condition encountered."
    },
    {
        "name": "EXCEPTION_FAULT",
        "severity": "ERROR",
        "category": "Hardware / Fault",
        "regex": r"(?:data\s+abort|prefetch\s+abort|segmentation\s+fault|page\s+fault\s+at)",
        "description": "Hardware memory or bus exception."
    },
    {
        "name": "SYSCON_ERROR_CODE",
        "severity": "ERROR",
        "category": "Syscon / Power Management",
        "regex": r"(?:SYSCON.*(?:ERR|ERROR|FAULT)[^0-9a-fA-F]*([0-9A-Fa-f]{4,8})|err:\s*([0-9A-Fa-f]{4,8}))",
        "description": "Syscon power sequencing or hardware error code (verify against service manual)."
    },
    {
        "name": "THERMAL_ALERT",
        "severity": "WARNING",
        "category": "Thermal",
        "regex": r"(?:thermal.*(?:overheat|high|throttl)|overheat\s+protection)",
        "description": "Thermal threshold warning or temperature protection triggered."
    },
    {
        "name": "I2C_SPI_TIMEOUT",
        "severity": "WARNING",
        "category": "Bus Communication",
        "regex": r"(?:i2c[0-9]*\s*timeout|spi[0-9]*\s*timeout|bus\s+arbitration\s+lost)",
        "description": "Peripheral bus timeout or Southbridge communication error."
    },
    {
        "name": "AUTHENTICATION_FAIL",
        "severity": "CRITICAL",
        "category": "Security / Bootloader",
        "regex": r"(?:signature\s+verification\s+failed|auth\s+failed|security\s+descriptor\s+invalid)",
        "description": "Cryptographic signature check failure during boot stage."
    }
]

# Known public community error code hints (explicitly documented as community mappings, not official Sony claims)
COMMUNITY_SYSCON_CODES = {
    "00000000": "OK / Normal shutdown status",
    "80801000": "Power rail standby state (Standard standby sequencing)",
    "80801300": "APU power rail nominal signal",
    "80801400": "Thermal warning flag logged",
    "80801500": "Fan controller communication error",
}

class DiagnosticLogAnalyzer:
    """Parses text diagnostic logs, extracts anomalies, and groups repeated events."""

    def __init__(self, custom_rules: Optional[List[Dict[str, Any]]] = None):
        self.rules = custom_rules or DEFAULT_PATTERNS

    def analyze_file(self, file_path: Path, context_radius: int = 2) -> Dict[str, Any]:
        if not file_path.exists():
            raise FileNotFoundError(f"Log file not found: {file_path}")

        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
        matches: List[DiagnosticMatch] = []
        message_counts: Dict[str, int] = {}

        timestamp_regex = re.compile(r"^\[?(\d{4}[-/]\d{2}[-/]\d{2}[\sT]\d{2}:\d{2}:\d{2}(?:\.\d+)?|\d+\.\d+)\]?")

        for idx, line in enumerate(lines):
            clean_line = line.strip()
            if not clean_line:
                continue

            # Group repeated messages
            simplified = re.sub(r"\d+", "<NUM>", clean_line)
            message_counts[simplified] = message_counts.get(simplified, 0) + 1

            # Check timestamp
            ts_match = timestamp_regex.search(clean_line)
            norm_ts = ts_match.group(1) if ts_match else None

            # Test rules
            for r in self.rules:
                found = re.search(r["regex"], clean_line, re.IGNORECASE)
                if found:
                    code_extracted = None
                    # If regex has capture groups
                    if found.groups():
                        code_extracted = next((g for g in found.groups() if g), None)

                    code_desc = r["description"]
                    if code_extracted:
                        hint = COMMUNITY_SYSCON_CODES.get(code_extracted.upper())
                        if hint:
                            code_desc += f" [Community Note: {hint}]"
                        else:
                            code_desc += f" [Unknown Code 0x{code_extracted}: User mapping required]"

                    ctx_before = lines[max(0, idx - context_radius):idx]
                    ctx_after = lines[idx + 1:min(len(lines), idx + 1 + context_radius)]

                    matches.append(DiagnosticMatch(
                        rule_name=r["name"],
                        severity=r["severity"],
                        line_number=idx + 1,
                        raw_line=clean_line,
                        normalized_timestamp=norm_ts,
                        category=r["category"],
                        description=code_desc,
                        code=code_extracted,
                        context_before=ctx_before,
                        context_after=ctx_after
                    ))

        # Sort repeated groups
        frequent_messages = sorted(
            [{"pattern": k, "occurrences": v} for k, v in message_counts.items() if v > 1],
            key=lambda x: x["occurrences"],
            reverse=True
        )[:10]

        severity_counts = {
            "CRITICAL": sum(1 for m in matches if m.severity == "CRITICAL"),
            "ERROR": sum(1 for m in matches if m.severity == "ERROR"),
            "WARNING": sum(1 for m in matches if m.severity == "WARNING"),
            "NOTICE": sum(1 for m in matches if m.severity == "NOTICE"),
        }

        return {
            "file_name": file_path.name,
            "total_lines": len(lines),
            "anomalies_detected": len(matches),
            "severity_summary": severity_counts,
            "frequent_messages": frequent_messages,
            "matches": [asdict(m) for m in matches]
        }
