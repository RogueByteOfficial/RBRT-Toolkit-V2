"""Local environment and diagnostic health verification module for RogueByte RBRT Toolkit V2."""

import sys
import os
import platform
import shutil
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from rbrt.utils.styling import styler
from rbrt.config import get_config

@dataclass
class DiagnosticCheck:
    name: str
    status: str  # PASS, WARN, FAIL, INFO
    category: str
    details: str
    remediation: Optional[str] = None

class RBRTDoctor:
    """Executes genuine local environment diagnostic checks."""

    def __init__(self, workspace: Optional[Path] = None):
        self.workspace = workspace or Path.cwd()
        self.checks: List[DiagnosticCheck] = []

    def run_all(self) -> List[DiagnosticCheck]:
        self.checks.clear()
        self._check_os_and_kernel()
        self._check_python_runtime()
        self._check_virtual_env()
        self._check_python_packages()
        self._check_workspace_permissions_and_disk()
        self._check_system_tools()
        self._check_serial_subsystem()
        self._check_project_dirs_and_fixtures()
        return self.checks

    def _check_os_and_kernel(self) -> None:
        os_name = platform.system()
        kernel = platform.release()
        arch = platform.machine()
        distro = "Unknown"

        if os_name == "Linux":
            try:
                if Path("/etc/os-release").exists():
                    with open("/etc/os-release") as f:
                        for line in f:
                            if line.startswith("PRETTY_NAME="):
                                distro = line.split("=", 1)[1].strip().strip('"')
                                break
            except Exception:
                distro = "Linux Generic"
            status = "PASS"
            details = f"{distro} (Kernel: {kernel}, Arch: {arch})"
            remed = None
        elif os_name == "Windows":
            status = "PASS"
            details = f"Windows {platform.version()} ({arch})"
            remed = "Ensure pyserial is installed for Windows COM port compatibility."
        elif os_name == "Darwin":
            status = "WARN"
            details = f"macOS {platform.mac_ver()[0]} ({arch})"
            remed = "UART devices typically appear under /dev/cu.* on macOS."
        else:
            status = "WARN"
            details = f"Operating System: {os_name} ({arch})"
            remed = "Non-standard environment. Core file operations supported; hardware serial depends on OS driver."

        self.checks.append(DiagnosticCheck(
            name="Operating System & Distribution",
            status=status,
            category="System",
            details=details,
            remediation=remed
        ))

    def _check_python_runtime(self) -> None:
        ver = sys.version_info
        ver_str = f"{ver.major}.{ver.minor}.{ver.micro}"
        if ver.major == 3 and ver.minor >= 11:
            status = "PASS"
            remed = None
        elif ver.major == 3 and ver.minor >= 10:
            status = "PASS"
            remed = "Python 3.10 is supported. Python 3.11+ recommended for enhanced standard library features."
        else:
            status = "FAIL"
            remed = "Install Python 3.10+ (preferred 3.11 or newer)."

        self.checks.append(DiagnosticCheck(
            name="Python Version",
            status=status,
            category="Runtime",
            details=f"Python {ver_str} ({sys.executable})",
            remediation=remed
        ))

    def _check_virtual_env(self) -> None:
        is_venv = (sys.prefix != getattr(sys, "base_prefix", sys.prefix)) or ("VIRTUAL_ENV" in os.environ)
        if is_venv:
            venv_path = os.environ.get("VIRTUAL_ENV", sys.prefix)
            self.checks.append(DiagnosticCheck(
                name="Python Virtual Environment",
                status="PASS",
                category="Runtime",
                details=f"Active virtual environment at {venv_path}",
                remediation=None
            ))
        else:
            self.checks.append(DiagnosticCheck(
                name="Python Virtual Environment",
                status="INFO",
                category="Runtime",
                details="Running under global/system Python environment.",
                remediation="Recommended: create virtual environment with 'python3 -m venv .venv && source .venv/bin/activate'."
            ))

    def _check_python_packages(self) -> None:
        # Check standard library modules
        try:
            import hashlib
            import difflib
            import struct
            self.checks.append(DiagnosticCheck(
                name="Standard Library Modules (hashlib, difflib, struct)",
                status="PASS",
                category="Dependencies",
                details="Core binary and cryptographic modules verified.",
            ))
        except ImportError as e:
            self.checks.append(DiagnosticCheck(
                name="Standard Library Modules",
                status="FAIL",
                category="Dependencies",
                details=f"Missing standard library component: {e}",
                remediation="Reinstall standard python3 library components."
            ))

        # Check optional dependencies: rich, serial, pyelftools
        packages = [
            ("rich", "Rich Terminal UI", "Optional: enhanced color formatting and tables"),
            ("serial", "pySerial", "Optional for file analysis; Required for live physical UART hardware"),
            ("elftools", "pyelftools", "Optional: advanced DWARF/relocation inspection; native ELF fallback active"),
            ("pytest", "pytest", "Optional: run pytest automated tests")
        ]
        for mod, label, note in packages:
            try:
                __import__(mod)
                self.checks.append(DiagnosticCheck(
                    name=f"Dependency: {label}",
                    status="PASS",
                    category="Dependencies",
                    details=f"Module '{mod}' is installed and operational.",
                ))
            except ImportError:
                self.checks.append(DiagnosticCheck(
                    name=f"Dependency: {label}",
                    status="INFO",
                    category="Dependencies",
                    details=f"Module '{mod}' not detected. ({note})",
                    remediation=f"Install with: pip install {mod}"
                ))

    def _check_workspace_permissions_and_disk(self) -> None:
        # Check read/write permission
        test_file = self.workspace / ".rbrt_perm_check.tmp"
        can_write = False
        try:
            test_file.write_text("rbrt-check")
            test_file.unlink(missing_ok=True)
            can_write = True
        except Exception as e:
            can_write = False
            err_msg = str(e)

        if can_write:
            self.checks.append(DiagnosticCheck(
                name="Workspace Filesystem Permissions",
                status="PASS",
                category="Filesystem",
                details=f"Read and write permissions confirmed for {self.workspace}",
            ))
        else:
            self.checks.append(DiagnosticCheck(
                name="Workspace Filesystem Permissions",
                status="FAIL",
                category="Filesystem",
                details=f"Cannot write to workspace: {err_msg}",
                remediation=f"Check folder permissions or grant write access to {self.workspace}."
            ))

        # Check disk space
        try:
            total, used, free = shutil.disk_usage(self.workspace)
            free_gb = free / (1024 ** 3)
            if free_gb >= 2.0:
                status = "PASS"
                remed = None
            elif free_gb >= 0.5:
                status = "WARN"
                remed = "Firmware dump comparison can require several gigabytes. Free up disk space."
            else:
                status = "FAIL"
                remed = "Critical low disk space. Ensure at least 1GB is available for dump analysis."

            self.checks.append(DiagnosticCheck(
                name="Available Disk Storage",
                status=status,
                category="Filesystem",
                details=f"{free_gb:.2f} GB free of {total / (1024 ** 3):.2f} GB total",
                remediation=remed
            ))
        except Exception as e:
            self.checks.append(DiagnosticCheck(
                name="Available Disk Storage",
                status="WARN",
                category="Filesystem",
                details=f"Unable to query disk metrics: {e}",
            ))

    def _check_system_tools(self) -> None:
        tools = ["sha256sum", "readelf", "file"]
        for tool in tools:
            tool_path = shutil.which(tool)
            if tool_path:
                self.checks.append(DiagnosticCheck(
                    name=f"System Utility: '{tool}'",
                    status="PASS",
                    category="System Tools",
                    details=f"Found at {tool_path}",
                ))
            else:
                self.checks.append(DiagnosticCheck(
                    name=f"System Utility: '{tool}'",
                    status="INFO",
                    category="System Tools",
                    details=f"'{tool}' not found in PATH (Toolkit uses native Python fallback).",
                    remediation=f"Optional: install on Linux via 'sudo apt install binutils file coreutils'."
                ))

    def _check_serial_subsystem(self) -> None:
        # Check UART driver & port discovery capability
        from rbrt.uart.serial_manager import list_available_ports
        ports, error = list_available_ports()
        if error:
            self.checks.append(DiagnosticCheck(
                name="Serial Hardware Discovery",
                status="WARN",
                category="Hardware UART",
                details=f"Port enumeration notice: {error}",
                remediation="Verify user belongs to 'dialout'/'uucp' group or install pyserial."
            ))
        else:
            p_desc = f"{len(ports)} port(s) detected: " + ", ".join(p["device"] for p in ports) if ports else "0 active physical serial ports detected (Normal when no USB UART adapter is plugged in)."
            self.checks.append(DiagnosticCheck(
                name="Serial Hardware Discovery",
                status="PASS",
                category="Hardware UART",
                details=p_desc,
                remediation=None if ports else "Plug in a 3.3V/1.8V FTDI/CP2102/CH340 adapter when ready for hardware logging."
            ))

    def _check_project_dirs_and_fixtures(self) -> None:
        cfg = get_config()
        rep_dir = cfg.reports_dir
        exists = rep_dir.exists()
        self.checks.append(DiagnosticCheck(
            name="Reports Output Directory",
            status="PASS" if exists else "INFO",
            category="Configuration",
            details=f"Reports location: {rep_dir} ({'Ready' if exists else 'Will be created automatically'})",
        ))

        # Check test fixtures
        fixtures_dir = self.workspace / "tests" / "fixtures"
        has_fixtures = fixtures_dir.exists() and any(fixtures_dir.iterdir()) if fixtures_dir.exists() else False
        self.checks.append(DiagnosticCheck(
            name="Test Fixtures Availability",
            status="PASS" if has_fixtures else "INFO",
            category="Diagnostics",
            details=f"Synthetic test fixtures: {'Available' if has_fixtures else 'Auto-generated on demand by test runner'}",
        ))

    def format_text_report(self) -> str:
        lines: List[str] = []
        lines.append(styler.banner())
        lines.append(f"{styler.BOLD}ENVIRONMENT & DIAGNOSTIC AUDIT REPORT{styler.RESET}\n")

        headers = ["Status", "Category", "Diagnostic Check", "Details"]
        rows = []
        for c in self.checks:
            rows.append([
                styler.badge(c.status),
                c.category,
                c.name,
                c.details
            ])
        
        styler.print_table("RBRT Doctor Health Assessment", headers, rows)

        # Show remediation items if any FAIL or WARN exist
        warnings = [c for c in self.checks if c.status in ("FAIL", "WARN") and c.remediation]
        if warnings:
            print(f"\n{styler.BOLD}{styler.YELLOW}Remediation Suggestions:{styler.RESET}")
            for w in warnings:
                print(f" • {styler.BOLD}{w.name}{styler.RESET}: {w.remediation}")
            print()

        pass_count = sum(1 for c in self.checks if c.status == "PASS")
        warn_count = sum(1 for c in self.checks if c.status == "WARN")
        fail_count = sum(1 for c in self.checks if c.status == "FAIL")
        info_count = sum(1 for c in self.checks if c.status == "INFO")

        summary = f"Audit complete: {pass_count} Passed, {warn_count} Warnings, {fail_count} Failed, {info_count} Informational."
        return summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "toolkit": "RogueByte RBRT Toolkit V2",
            "checks": [asdict(c) for c in self.checks],
            "summary": {
                "pass": sum(1 for c in self.checks if c.status == "PASS"),
                "warn": sum(1 for c in self.checks if c.status == "WARN"),
                "fail": sum(1 for c in self.checks if c.status == "FAIL"),
                "info": sum(1 for c in self.checks if c.status == "INFO"),
            }
        }
