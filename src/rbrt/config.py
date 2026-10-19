"""RBRT Toolkit V2 Configuration and Paths."""

import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ToolkitConfig:
    workspace_dir: Path
    reports_dir: Path
    logs_dir: Path
    default_baud: int = 115200
    chunk_size: int = 65536  # 64 KB for chunked hashing and comparison
    max_preview_bytes: int = 512
    safe_uart_mode: bool = True  # Read-only UART by default
    require_explicit_flash: bool = True

def get_default_workspace() -> Path:
    """Returns workspace root path, checking environment or project root."""
    env_ws = os.environ.get("RBRT_WORKSPACE")
    if env_ws:
        p = Path(env_ws).resolve()
    else:
        # Check current working directory or package root
        p = Path.cwd().resolve()
    return p

def get_config() -> ToolkitConfig:
    """Initializes and returns active ToolkitConfig."""
    ws = get_default_workspace()
    reports = ws / "reports"
    logs = ws / "logs"
    return ToolkitConfig(
        workspace_dir=ws,
        reports_dir=reports,
        logs_dir=logs,
    )

def ensure_directories(config: ToolkitConfig) -> None:
    """Ensures workspace directories exist with safe permissions."""
    config.reports_dir.mkdir(parents=True, exist_ok=True)
    config.logs_dir.mkdir(parents=True, exist_ok=True)
