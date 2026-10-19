"""Command-line interface routing and subcommands for RogueByte RBRT Toolkit V2."""

import argparse
import sys
import json
from pathlib import Path
from typing import List, Optional

from rbrt import __version__, TOOLKIT_NAME
from rbrt.utils.styling import styler
from rbrt.doctor import RBRTDoctor
from rbrt.device import print_device_info, get_environment_info
from rbrt.uart.serial_manager import list_available_ports, UARTConsole
from rbrt.bin_tools.analyzer import inspect_binary_file, compare_binary_files
from rbrt.elf.parser import analyze_elf_file, compare_elf_files
from rbrt.pup.inspector import inspect_pup_file, compare_pup_files
from rbrt.dump.manager import DumpManager
from rbrt.reports.generator import list_existing_reports, ReportGenerator

def build_parser() -> argparse.ArgumentParser:
    """Builds the comprehensive argument parser for rbrt CLI."""
    parser = argparse.ArgumentParser(
        prog="rbrt",
        description=f"{TOOLKIT_NAME} (v{__version__})\nCross-platform hardware diagnostics, serial console logging, firmware inspection, binary comparison, and ELF analysis toolkit.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Developer & Support:\n"
            "  Website: https://roguebyte.online\n"
            "  GitHub:  https://github.com/RogueByteOfficial/RBRT-Toolkit-V2\n"
            "  Sponsor: https://ko-fi.com/roguebyte\n"
            "  Email:   contact@roguebyte.online\n"
        )
    )
    parser.add_argument("-v", "--version", action="version", version=f"{TOOLKIT_NAME} v{__version__}")

    subparsers = parser.add_subparsers(dest="subcommand", title="Commands", description="Available rbrt commands")

    # doctor
    p_doctor = subparsers.add_parser("doctor", help="Inspect local environment, toolchains, permissions, and dependencies.")
    p_doctor.add_argument("--json", action="store_true", help="Output machine-readable JSON result.")
    p_doctor.add_argument("--report", type=str, help="Save diagnosis to specific report file path.")

    # device
    p_device = subparsers.add_parser("device", help="Display host system, kernel, CPU architecture, and runtime details.")
    p_device.add_argument("--json", action="store_true", help="Output machine-readable JSON result.")

    # uart
    p_uart = subparsers.add_parser("uart", help="UART serial port enumeration, connection, and logging.")
    uart_sub = p_uart.add_subparsers(dest="uart_command", required=True)

    # uart ports
    uart_sub.add_parser("ports", help="Enumerate available serial ports.")

    # uart connect
    p_uart_conn = uart_sub.add_parser("connect", help="Open a read-only serial console connection.")
    p_uart_conn.add_argument("--port", required=True, help="Serial device port name (e.g. /dev/ttyUSB0, COM3, or MOCK).")
    p_uart_conn.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200).")
    p_uart_conn.add_argument("--mock", action="store_true", help="Use local mock serial backend for testing.")

    # uart log
    p_uart_log = uart_sub.add_parser("log", help="Capture incoming UART serial data to timestamped log file.")
    p_uart_log.add_argument("--port", required=True, help="Serial device port name.")
    p_uart_log.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200).")
    p_uart_log.add_argument("--output", required=True, help="Path to destination log file.")
    p_uart_log.add_argument("--duration", type=float, default=None, help="Capture timeout duration in seconds.")
    p_uart_log.add_argument("--mock", action="store_true", help="Use local mock serial backend for testing.")

    # bin
    p_bin = subparsers.add_parser("bin", help="Binary file inspection and chunk-based comparison.")
    bin_sub = p_bin.add_subparsers(dest="bin_command", required=True)

    p_bin_insp = bin_sub.add_parser("inspect", help="Inspect binary file size, SHA-256, format signature, and hex preview.")
    p_bin_insp.add_argument("file", help="Path to binary file.")
    p_bin_insp.add_argument("--json", action="store_true", help="Output in JSON format.")
    p_bin_insp.add_argument("--report", type=str, help="Save report to file.")

    p_bin_comp = bin_sub.add_parser("compare", help="Compare two binary files byte-by-byte in chunks.")
    p_bin_comp.add_argument("file_a", help="First binary file.")
    p_bin_comp.add_argument("file_b", help="Second binary file.")
    p_bin_comp.add_argument("--json", action="store_true", help="Output in JSON format.")
    p_bin_comp.add_argument("--report", type=str, help="Save report to file.")

    # elf
    p_elf = subparsers.add_parser("elf", help="ELF binary structure, architecture, symbols, and section inspection.")
    elf_sub = p_elf.add_subparsers(dest="elf_command", required=True)

    p_elf_ana = elf_sub.add_parser("analyze", help="Analyze ELF binary header, sections, segments, and symbols.")
    p_elf_ana.add_argument("file", help="Path to ELF binary.")
    p_elf_ana.add_argument("--json", action="store_true", help="Output in JSON format.")
    p_elf_ana.add_argument("--report", type=str, help="Save report to file.")

    p_elf_comp = elf_sub.add_parser("compare", help="Compare section tables and architecture of two ELF files.")
    p_elf_comp.add_argument("file_a", help="First ELF binary.")
    p_elf_comp.add_argument("file_b", help="Second ELF binary.")
    p_elf_comp.add_argument("--json", action="store_true", help="Output in JSON format.")
    p_elf_comp.add_argument("--report", type=str, help="Save report to file.")

    # pup
    p_pup = subparsers.add_parser("pup", help="PlayStation Update Package (PUP) outer container inspector.")
    pup_sub = p_pup.add_subparsers(dest="pup_command", required=True)

    p_pup_insp = pup_sub.add_parser("inspect", help="Inspect PUP SCE container signature, versions, and entry table.")
    p_pup_insp.add_argument("file", help="Path to PUP file.")
    p_pup_insp.add_argument("--json", action="store_true", help="Output in JSON format.")
    p_pup_insp.add_argument("--report", type=str, help="Save report to file.")

    p_pup_comp = pup_sub.add_parser("compare", help="Compare two PUP firmware containers.")
    p_pup_comp.add_argument("file_a", help="First PUP file.")
    p_pup_comp.add_argument("file_b", help="Second PUP file.")
    p_pup_comp.add_argument("--json", action="store_true", help="Output in JSON format.")
    p_pup_comp.add_argument("--report", type=str, help="Save report to file.")

    # dump
    p_dump = subparsers.add_parser("dump", help="Manage and inspect user-supplied flash/firmware dumps non-destructively.")
    dump_sub = p_dump.add_subparsers(dest="dump_command", required=True)

    p_dump_insp = dump_sub.add_parser("inspect", help="Inspect and catalog a user-provided binary dump.")
    p_dump_insp.add_argument("file", help="Path to binary dump file.")
    p_dump_insp.add_argument("--model", type=str, help="Console model designation (e.g. CUH-1215, CFI-1015).")
    p_dump_insp.add_argument("--board", type=str, help="Board revision (e.g. SAC-001, EDM-020).")
    p_dump_insp.add_argument("--notes", type=str, help="Acquisition notes.")
    p_dump_insp.add_argument("--json", action="store_true", help="Output in JSON format.")

    # report
    p_rep = subparsers.add_parser("report", help="Report history and export management.")
    rep_sub = p_rep.add_subparsers(dest="report_command", required=True)
    rep_sub.add_parser("list", help="List all generated reports.")
    p_rep_exp = rep_sub.add_parser("export", help="Export latest report to specific destination.")
    p_rep_exp.add_argument("--format", choices=["json", "txt", "md"], default="json", help="Export format.")
    p_rep_exp.add_argument("--output", type=str, help="Target destination filename.")

    return parser


def handle_cli(args: Optional[List[str]] = None) -> int:
    """Executes CLI command and returns process exit code."""
    parser = build_parser()
    parsed = parser.parse_args(args)

    if not parsed.subcommand:
        # Launch interactive menu if interactive TTY or no command passed
        if sys.stdin.isatty():
            from rbrt.terminal_ui import TerminalUI
            ui = TerminalUI()
            ui.run_menu()
            return 0
        else:
            parser.print_help()
            return 0

    try:
        # DOCTOR
        if parsed.subcommand == "doctor":
            doc = RBRTDoctor()
            doc.run_all()
            if parsed.json:
                print(json.dumps(doc.to_dict(), indent=2))
            else:
                summary = doc.format_text_report()
                print(f"{styler.BOLD}{summary}{styler.RESET}")

            if parsed.report:
                rep_path = Path(parsed.report)
                rep_path.parent.mkdir(parents=True, exist_ok=True)
                rep_path.write_text(json.dumps(doc.to_dict(), indent=2), encoding="utf-8")
                print(f"{styler.badge('INFO')} Diagnostic report saved to: {rep_path}")

            # Exit code convention: 0 if no fatal errors, 1 if any check FAIL
            has_fail = any(c.status == "FAIL" for c in doc.checks)
            return 1 if has_fail else 0

        # DEVICE
        elif parsed.subcommand == "device":
            if parsed.json:
                print(json.dumps(get_environment_info(), indent=2))
            else:
                print_device_info()
            return 0

        # UART
        elif parsed.subcommand == "uart":
            if parsed.uart_command == "ports":
                ports, err = list_available_ports()
                if err:
                    print(f"{styler.badge('WARN')} {err}")
                headers = ["Port", "Description", "Hardware ID"]
                rows = [[p["device"], p["description"], p["hwid"]] for p in ports]
                styler.print_table("Available Serial Ports", headers, rows)
                return 0

            elif parsed.uart_command == "connect":
                console = UARTConsole(port=parsed.port, baud=parsed.baud, mock_mode=parsed.mock)
                ok, msg = console.connect()
                if not ok:
                    print(f"{styler.badge('FAIL')} {msg}")
                    return 1
                print(f"{styler.badge('PASS')} {msg}")
                console.stream_and_log()
                console.close()
                return 0

            elif parsed.uart_command == "log":
                out_path = Path(parsed.output)
                console = UARTConsole(port=parsed.port, baud=parsed.baud, mock_mode=parsed.mock)
                ok, msg = console.connect()
                if not ok:
                    print(f"{styler.badge('FAIL')} {msg}")
                    return 1
                stats = console.stream_and_log(output_file=out_path, max_duration_sec=parsed.duration)
                console.close()
                print(f"\n{styler.badge('PASS')} UART log capture saved to {out_path} ({stats['lines_captured']} lines, {stats['bytes_received']} bytes).")
                return 0

        # BIN
        elif parsed.subcommand == "bin":
            if parsed.bin_command == "inspect":
                p = Path(parsed.file)
                res = inspect_binary_file(p)
                if parsed.json:
                    from dataclasses import asdict
                    print(json.dumps(asdict(res), indent=2))
                else:
                    headers = ["Property", "Value"]
                    rows = [
                        ["File", res.file_name],
                        ["Size", f"{res.size_bytes:,} B ({res.size_human})"],
                        ["SHA-256", res.sha256],
                        ["Type Signature", res.format_hint],
                        ["Entropy", f"{res.entropy_estimate:.4f} bits/byte"],
                        ["Repetition Check", "Repeated filler detected" if res.is_repetitive else "Normal variation"],
                    ]
                    styler.print_table(f"BIN Inspection: {res.file_name}", headers, rows)
                    if res.truncation_warning:
                        print(f"{styler.badge('WARN')} {res.truncation_warning}")
                    print(f"\n{styler.BOLD}First 128 Bytes Preview:{styler.RESET}\n{res.preview_hex}")

                if parsed.report:
                    rep = ReportGenerator("bin_inspect")
                    rep.add_input_file(p, sha256=res.sha256, size=res.size_bytes)
                    if res.truncation_warning:
                        rep.add_warning(res.truncation_warning)
                    rep.details = asdict(res)
                    out_r = rep.save(custom_destination=Path(parsed.report))
                    print(f"{styler.badge('INFO')} Report saved to: {out_r}")
                return 0

            elif parsed.bin_command == "compare":
                pa, pb = Path(parsed.file_a), Path(parsed.file_b)
                res = compare_binary_files(pa, pb)
                if parsed.json:
                    from dataclasses import asdict
                    print(json.dumps(asdict(res), indent=2))
                else:
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
                return 0

        # ELF
        elif parsed.subcommand == "elf":
            if parsed.elf_command == "analyze":
                p = Path(parsed.file)
                res = analyze_elf_file(p)
                if parsed.json:
                    from dataclasses import asdict
                    print(json.dumps(asdict(res), indent=2))
                else:
                    if not res.is_valid_elf:
                        print(f"{styler.badge('FAIL')} Not a valid ELF: {res.error}")
                        return 1
                    headers = ["Header Field", "Value"]
                    rows = [
                        ["Architecture", str(res.machine_arch)],
                        ["Bitness", str(res.bitness)],
                        ["Endianness", str(res.endianness)],
                        ["Type", str(res.object_type)],
                        ["Entry Point", str(res.entry_point)],
                        ["Sections", str(len(res.sections))],
                        ["Segments", str(len(res.segments))],
                        ["Symbols Estimated", str(res.symbols_count)],
                        ["Stripped", "YES" if res.is_stripped else "NO"],
                        ["Parser Engine", res.parser_used]
                    ]
                    styler.print_table(f"ELF Analysis: {res.file_name}", headers, rows)

                if parsed.report:
                    from dataclasses import asdict
                    rep = ReportGenerator("elf_analyze")
                    rep.add_input_file(p, sha256=res.sha256, size=res.file_size)
                    rep.details = asdict(res)
                    out_r = rep.save(custom_destination=Path(parsed.report))
                    print(f"{styler.badge('INFO')} Report saved to: {out_r}")
                return 0

            elif parsed.elf_command == "compare":
                pa, pb = Path(parsed.file_a), Path(parsed.file_b)
                comp = compare_elf_files(pa, pb)
                if parsed.json:
                    print(json.dumps(comp, indent=2))
                else:
                    headers = ["ELF Metric", "Comparison Result"]
                    rows = [
                        ["Architecture Match", "YES" if comp["arch_match"] else f"NO ({comp['arch_a']} vs {comp['arch_b']})"],
                        ["Entry Point Match", "YES" if comp["entry_point_match"] else f"NO ({comp['entry_a']} vs {comp['entry_b']})"],
                        ["Modified Sections", str(comp["modified_sections_count"])],
                        ["Unique to File A", ", ".join(comp["sections_only_in_a"]) or "None"],
                        ["Unique to File B", ", ".join(comp["sections_only_in_b"]) or "None"],
                        ["Summary", comp["summary"]]
                    ]
                    styler.print_table("ELF Section Comparison", headers, rows)
                return 0

        # PUP
        elif parsed.subcommand == "pup":
            if parsed.pup_command == "inspect":
                p = Path(parsed.file)
                res = inspect_pup_file(p)
                if parsed.json:
                    from dataclasses import asdict
                    print(json.dumps(asdict(res), indent=2))
                else:
                    headers = ["PUP Parameter", "Value"]
                    rows = [
                        ["Valid SCE Container", "YES" if res.is_valid_pup_container else "NO"],
                        ["Magic", res.magic_hex],
                        ["Package Version", str(res.package_version)],
                        ["File Entries", str(res.file_entries_count)],
                        ["Encrypted Payloads", "YES (Expected)" if res.encrypted_payload_detected else "NO"],
                        ["Extraction Capability", "UNSUPPORTED (Proprietary keys omitted by design)" if not res.extraction_supported else "Supported"]
                    ]
                    styler.print_table(f"PUP Inspection: {res.file_name}", headers, rows)
                    for n in res.status_notes:
                        print(f" • {n}")
                return 0

            elif parsed.pup_command == "compare":
                pa, pb = Path(parsed.file_a), Path(parsed.file_b)
                comp = compare_pup_files(pa, pb)
                if parsed.json:
                    print(json.dumps(comp, indent=2))
                else:
                    headers = ["PUP Metric", "Value"]
                    rows = [
                        ["Binary Identical", "YES" if comp["binary_identical"] else "NO"],
                        ["Package Version Match", "YES" if comp["package_version_match"] else "NO"],
                        ["Differing Bytes", f"{comp['differing_bytes']:,} ({comp['differing_percentage']:.4f}%)"],
                        ["Summary", comp["summary"]]
                    ]
                    styler.print_table("PUP Comparison", headers, rows)
                return 0

        # DUMP
        elif parsed.subcommand == "dump":
            if parsed.dump_command == "inspect":
                p = Path(parsed.file)
                dm = DumpManager()
                rec = dm.register_dump(
                    p,
                    device_model=parsed.model,
                    board_revision=parsed.board,
                    source_notes=parsed.notes
                )
                if parsed.json:
                    from dataclasses import asdict
                    print(json.dumps(asdict(rec), indent=2))
                else:
                    headers = ["Dump Attribute", "Value"]
                    rows = [
                        ["Dump ID", rec.dump_id],
                        ["File Name", rec.file_name],
                        ["Size", f"{rec.size_bytes:,} bytes"],
                        ["SHA-256", rec.sha256],
                        ["Device Model", rec.device_model or "Not specified"],
                        ["Board Revision", rec.board_revision or "Not specified"],
                        ["Repetitive Filler", "YES (0x{:02X})".format(rec.repetitive_byte) if rec.is_repetitive and rec.repetitive_byte is not None else "Normal"]
                    ]
                    styler.print_table(f"Dump Cataloged: {rec.dump_id}", headers, rows)
                return 0

        # REPORT
        elif parsed.subcommand == "report":
            if parsed.report_command == "list":
                reps = list_existing_reports()
                print(f"\n{styler.badge('INFO')} Total reports found: {len(reps)}")
                if reps:
                    headers = ["Report File", "Size", "Modified"]
                    rows = [[r["name"], f"{r['size']} B", r["modified"][:19]] for r in reps]
                    styler.print_table("Forensic Reports Catalog", headers, rows)
                return 0
            elif parsed.report_command == "export":
                reps = list_existing_reports()
                if not reps:
                    print(f"{styler.badge('WARN')} No existing reports found to export.")
                    return 1
                latest = reps[0]
                print(f"{styler.badge('PASS')} Latest report: {latest['path']}")
                return 0

    except Exception as e:
        print(f"{styler.badge('FAIL')} Command error: {e}", file=sys.stderr)
        return 1

    return 0
