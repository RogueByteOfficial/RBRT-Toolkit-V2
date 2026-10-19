"""Terminal styling and formatted output for RogueByte RBRT Toolkit V2.
Gracefully utilizes 'rich' when installed, or falls back to standard ANSI styling.
"""

import sys
from typing import List, Tuple, Optional, Any

# Try importing rich
try:
    from rich.console import Console as RichConsole
    from rich.table import Table as RichTable
    from rich.panel import Panel as RichPanel
    from rich.text import Text as RichText
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

class TerminalStyler:
    """Provides consistent ANSI / Rich formatting and status indicators."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_DARK = "\033[40m"

    def __init__(self, force_ansi: bool = True):
        self.rich_console = RichConsole() if _HAS_RICH else None
        self.use_color = force_ansi or sys.stdout.isatty()

    def badge(self, status: str) -> str:
        """Returns colored status indicator [PASS], [WARN], [FAIL], [INFO]."""
        s = status.upper().strip()
        if not self.use_color:
            return f"[{s}]"

        if s == "PASS":
            return f"{self.BOLD}{self.GREEN}[ PASS ]{self.RESET}"
        elif s == "WARN":
            return f"{self.BOLD}{self.YELLOW}[ WARN ]{self.RESET}"
        elif s == "FAIL":
            return f"{self.BOLD}{self.RED}[ FAIL ]{self.RESET}"
        elif s == "INFO":
            return f"{self.BOLD}{self.CYAN}[ INFO ]{self.RESET}"
        else:
            return f"[{s}]"

    def banner(self) -> str:
        """Returns the RogueByte RBRT Toolkit V2 startup banner."""
        banner_text = (
            f"{self.BOLD}{self.CYAN}"
            f"╔════════════════════════════════════════════════════════════════════════╗\n"
            f"║                            ROGUEBYTE                                   ║\n"
            f"║                        RBRT TOOLKIT V2                                 ║\n"
            f"║         Hardware Diagnostics | Firmware Analysis | Digital Forensics   ║\n"
            f"╚════════════════════════════════════════════════════════════════════════╝\n"
            f"{self.RESET}"
            f"{self.DIM}   Website: https://roguebyte.online  |  Contact: contact@roguebyte.online{self.RESET}\n"
        )
        return banner_text

    def print_banner(self) -> None:
        print(self.banner())

    def print_table(self, title: str, headers: List[str], rows: List[List[Any]]) -> None:
        """Prints a clean tabular layout."""
        if _HAS_RICH and self.rich_console:
            table = RichTable(title=title, header_style="bold cyan", border_style="dim")
            for h in headers:
                table.add_column(h)
            for row in rows:
                table.add_row(*[str(cell) for cell in row])
            self.rich_console.print(table)
            return

        # Fallback ANSI table
        print(f"\n{self.BOLD}{self.CYAN}{title}{self.RESET}")
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
        print(sep)
        header_row = "| " + " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths)) + " |"
        print(f"{self.BOLD}{header_row}{self.RESET}")
        print(sep)
        for row in rows:
            line = "| " + " | ".join(f"{str(cell):<{w}}" for cell, w in zip(row, col_widths)) + " |"
            print(line)
        print(sep + "\n")

    def print_panel(self, text: str, title: Optional[str] = None) -> None:
        if _HAS_RICH and self.rich_console:
            self.rich_console.print(RichPanel(text, title=title, border_style="cyan"))
            return
        
        t = f"── {title} " if title else ""
        border = f"{self.CYAN}┌{t.ljust(70, '─')}┐{self.RESET}"
        print(border)
        for line in text.splitlines():
            print(f"{self.CYAN}│{self.RESET} {line:<68} {self.CYAN}│{self.RESET}")
        print(f"{self.CYAN}└{'─'*70}┘{self.RESET}")

styler = TerminalStyler()
