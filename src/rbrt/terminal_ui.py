"""Interactive terminal user interface for RogueByte RBRT Toolkit V2."""

import sys
import os
from pathlib import Path
from typing import Optional

from rbrt.utils.styling import styler
from rbrt.doctor import RBRTDoctor
from rbrt.device import print_device_info, get_environment_info
from rbrt.uart.serial_manager import list_available_ports, UARTConsole
from rbrt.bin_tools.analyzer import inspect_binary_file, compare_binary_files
from rbrt.elf.parser import analyze_elf_file, compare_elf_files
from rbrt.pup.inspector import inspect_pup_file, compare_pup_files
from rbrt.dump.manager import DumpManager
from rbrt.diagnostics.log_analyzer import DiagnosticLogAnalyzer
from rbrt.reports.generator import list_existing_reports, ReportGenerator

class TerminalUI:
    """Manages the interactive terminal menu lifecycle and input validation."""

    def __init__(self):
        self.running = True

    def run_menu(self) -> None:
        """Runs the main interactive loop."""
        while self.running:
            try:
                self._display_main_screen()
                choice = input(f"\n{styler.BOLD}{styler.CYAN}rbrt > {styler.RESET}").strip()
                self._handle_choice(choice)
            except (KeyboardInterrupt, EOFError):
                print(f"\n\n{styler.badge('INFO')} Exiting RogueByte RBRT Toolkit V2. Goodbye.\n")
                self.running = False
                break

    def _display_main_screen(self) -> None:
        styler.print_banner()
        env = get_environment_info()
        print(f" {styler.BOLD}Environment:{styler.RESET} {env['os_name']} | Python {env['python_version']} | Arch: {env['architecture']}")

        deps_summary = []
        for k, v in env["optional_dependencies"].items():
            st = f"{styler.GREEN}✓{styler.RESET}" if v["installed"] else f"{styler.DIM}–{styler.RESET}"
            deps_summary.append(f"{k}: {st}")
        print(f" {styler.BOLD}Optional Modules:{styler.RESET} {'  '.join(deps_summary)}\n")

        menu = (
            f" {styler.BOLD}[1]{styler.RESET}  RBRT Doctor (Environment Diagnostics)\n"
            f" {styler.BOLD}[2]{styler.RESET}  Device & Environment Information\n"
            f" {styler.BOLD}[3]{styler.RESET}  UART Serial Console\n"
            f" {styler.BOLD}[4]{styler.RESET}  Console Diagnostic Logs\n"
            f" {styler.BOLD}[5]{styler.RESET}  BIN Analyzer & Comparator\n"
            f" {styler.BOLD}[6]{styler.RESET}  PUP Firmware Inspector\n"
            f" {styler.BOLD}[7]{styler.RESET}  ELF Analyzer\n"
            f" {styler.BOLD}[8]{styler.RESET}  Dump Manager\n"
            f" {styler.BOLD}[9]{styler.RESET}  Reports & Session History\n"
            f" {styler.BOLD}[10]{styler.RESET} Settings & Dependency Status\n"
            f" {styler.BOLD}[0]{styler.RESET}  Exit\n"
        )
        print(menu)

    def _handle_choice(self, choice: str) -> None:
        if choice in ("0", "exit", "quit", "q"):
            print(f"\n{styler.badge('INFO')} Exiting RogueByte RBRT Toolkit V2. Goodbye.\n")
            self.running = False
            return

        elif choice == "1":
            print(f"\n{styler.badge('INFO')} Running RBRT Doctor Diagnostics...\n")
            doc = RBRTDoctor()
            doc.run_all()
            summary = doc.format_text_report()
            print(f"{styler.BOLD}{summary}{styler.RESET}")

        elif choice == "2":
            print_device_info()

        elif choice == "3":
            self._menu_uart()

        elif choice == "4":
            self._menu_logs()

        elif choice == "5":
            self._menu_bin()

        elif choice == "6":
            self._menu_pup()

        elif choice == "7":
            self._menu_elf()

        elif choice == "8":
            self._menu_dump()

        elif choice == "9":
            self._menu_reports()

        elif choice == "10":
            self._menu_settings()

        else:
            print(f"{styler.badge('WARN')} Invalid selection '{choice}'. Please choose 0 through 10.")

        input(f"\n{styler.DIM}Press Enter to return to main menu...{styler.RESET}")

    def _menu_uart(self) -> None:
        ports, err = list_available_ports()
        headers = ["Index", "Port Device", "Description", "Hardware ID"]
        rows = []
        for i, p in enumerate(ports):
            rows.append([str(i + 1), p["device"], p["description"], p["hwid"]])
        rows.append(["M", "MOCK_PORT", "Local Mock Serial (Test / Emulation)", "Simulated"])
        styler.print_table("UART Serial Port Enumeration", headers, rows)

        target = input("Select port index or enter device path (or 'M' for mock): ").strip()
        baud_str = input("Enter baud rate (default: 115200): ").strip() or "115200"
        try:
            baud = int(baud_str)
        except ValueError:
            baud = 115200

        selected_device = "MOCK_PORT"
        if target.isdigit() and 1 <= int(target) <= len(ports):
            selected_device = ports[int(target) - 1]["device"]
        elif target.upper() != "M" and target:
            selected_device = target

        console = UARTConsole(port=selected_device, baud=baud, mock_mode=(selected_device == "MOCK_PORT"))
        ok, msg = console.connect()
        if not ok:
            print(f"{styler.badge('FAIL')} {msg}")
            return
        print(f"{styler.badge('PASS')} {msg}")
        console.stream_and_log(max_duration_sec=5.0 if selected_device == "MOCK_PORT" else None)
        console.close()

    def _menu_logs(self) -> None:
        fpath = input("Enter path to diagnostic text log: ").strip()
        if not fpath:
            return
        p = Path(fpath)
        if not p.exists():
            print(f"{styler.badge('FAIL')} File does not exist: {fpath}")
            return
        analyzer = DiagnosticLogAnalyzer()
        res = analyzer.analyze_file(p)
        print(f"\n{styler.badge('INFO')} Analyzed {res['total_lines']} lines in '{res['file_name']}'.")
        print(f"Anomalies detected: {res['anomalies_detected']}")
        for m in res["matches"]:
            print(f" [{m['severity']}] Line {m['line_number']}: {m['category']} - {m['description']}")
            print(f"   Raw: {m['raw_line']}")

    def _menu_bin(self) -> None:
        print("\n [1] Inspect Binary File")
        print(" [2] Compare Two Binary Files")
        sub = input("Selection: ").strip()
        if sub == "1":
            fpath = input("Enter binary file path: ").strip()
            if not fpath:
                return
            p = Path(fpath)
            if not p.exists():
                print(f"{styler.badge('FAIL')} File does not exist: {fpath}")
                return
            res = inspect_binary_file(p)
            headers = ["Property", "Value"]
            rows = [
                ["File Name", res.file_name],
                ["Size", f"{res.size_bytes:,} bytes ({res.size_human})"],
                ["SHA-256", res.sha256],
                ["Type Signature", res.format_hint],
                ["Entropy Estimate", f"{res.entropy_estimate:.4f} bits/byte"],
                ["Pattern Repetition", "YES (Unprogrammed Flash / Zeroed)" if res.is_repetitive else "Normal distribution"],
            ]
            styler.print_table(f"BIN Analysis: {res.file_name}", headers, rows)
            print(f"{styler.BOLD}Hex Preview (First 128 bytes):{styler.RESET}\n{res.preview_hex}")

        elif sub == "2":
            f_a = input("Path to File A: ").strip()
            f_b = input("Path to File B: ").strip()
            if not f_a or not f_b:
                return
            pa, pb = Path(f_a), Path(f_b)
            if not pa.exists() or not pb.exists():
                print(f"{styler.badge('FAIL')} One or both files not found.")
                return
            res = compare_binary_files(pa, pb)
            headers = ["Metric", "Comparison Result"]
            rows = [
                ["Status", "IDENTICAL" if res.identical else "DIVERGENT"],
                ["File A Size", f"{res.size_a:,} bytes"],
                ["File B Size", f"{res.size_b:,} bytes"],
                ["Differing Bytes", f"{res.differing_bytes_count:,} bytes ({res.differing_percentage:.4f}%)"],
                ["First Divergence", f"0x{res.first_diff_offset:08X}" if res.first_diff_offset is not None else "None"],
                ["Summary", res.summary]
            ]
            styler.print_table("Binary Difference Summary", headers, rows)

    def _menu_pup(self) -> None:
        fpath = input("Enter path to PUP firmware file: ").strip()
        if not fpath:
            return
        p = Path(fpath)
        if not p.exists():
            print(f"{styler.badge('FAIL')} File not found: {fpath}")
            return
        res = inspect_pup_file(p)
        headers = ["Field", "Value"]
        rows = [
            ["Valid SCE Container", "YES" if res.is_valid_pup_container else "NO"],
            ["Magic Hex", res.magic_hex],
            ["File Size", f"{res.file_size:,} bytes"],
            ["Package Version", str(res.package_version)],
            ["Entry Count", str(res.file_entries_count)],
            ["Encrypted Payloads", "Detected (Normal for retail packages)" if res.encrypted_payload_detected else "None"],
            ["Decryption Supported", "NO (Proprietary keys not bundled)" if not res.extraction_supported else "YES"]
        ]
        styler.print_table(f"PUP Inspection: {res.file_name}", headers, rows)
        for note in res.status_notes:
            print(f" • {note}")

    def _menu_elf(self) -> None:
        fpath = input("Enter path to ELF binary: ").strip()
        if not fpath:
            return
        p = Path(fpath)
        if not p.exists():
            print(f"{styler.badge('FAIL')} File not found: {fpath}")
            return
        res = analyze_elf_file(p)
        if not res.is_valid_elf:
            print(f"{styler.badge('FAIL')} Invalid ELF: {res.error}")
            return
        headers = ["Header Field", "Value"]
        rows = [
            ["Architecture", str(res.machine_arch)],
            ["Bitness", str(res.bitness)],
            ["Endianness", str(res.endianness)],
            ["Object Type", str(res.object_type)],
            ["Entry Point", str(res.entry_point)],
            ["Sections Count", str(len(res.sections))],
            ["Segments Count", str(len(res.segments))],
            ["Stripped Status", "Stripped" if res.is_stripped else "Symbol table present"],
            ["Parser Used", res.parser_used]
        ]
        styler.print_table(f"ELF Analysis: {res.file_name}", headers, rows)

    def _menu_dump(self) -> None:
        dm = DumpManager()
        dumps = dm.list_dumps()
        print(f"\n{styler.badge('INFO')} Total Registered Dumps in Manifest: {len(dumps)}")
        if dumps:
            headers = ["ID", "File Name", "Size", "SHA-256 (prefix)", "Imported At"]
            rows = [[d.dump_id, d.file_name, f"{d.size_bytes:,} B", d.sha256[:12] + "...", d.imported_at[:19]] for d in dumps]
            styler.print_table("Registered Dumps Catalog", headers, rows)
        print("To import a new dump: use 'rbrt dump inspect <file>' or register from CLI.")

    def _menu_reports(self) -> None:
        reports = list_existing_reports()
        print(f"\n{styler.badge('INFO')} Existing Forensic Reports: {len(reports)}")
        if reports:
            headers = ["Report File", "Size", "Last Modified"]
            rows = [[r["name"], f"{r['size']} B", r["modified"][:19]] for r in reports]
            styler.print_table("Generated Reports Directory", headers, rows)

    def _menu_settings(self) -> None:
        print_device_info()
