"""Device and operating environment information inspector."""

import platform
import sys
import os
import shutil
from typing import Dict, Any

from rbrt.utils.styling import styler

def get_environment_info() -> Dict[str, Any]:
    """Collects genuine system and runtime environment information."""
    info: Dict[str, Any] = {
        "os_name": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor() or "Unknown / Virtualized",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_executable": sys.executable,
        "is_64bit": sys.maxsize > 2**32,
        "byteorder": sys.byteorder,
        "working_directory": str(os.getcwd()),
    }

    # Detect Linux distribution if applicable
    if info["os_name"] == "Linux":
        distro = "Linux Generic"
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            distro = line.split("=", 1)[1].strip().strip('"')
                            break
        except Exception:
            pass
        info["distro"] = distro

    # Optional dependency presence
    deps = {}
    for mod in ["rich", "serial", "elftools", "pytest"]:
        try:
            m = __import__(mod)
            ver = getattr(m, "__version__", "Available")
            deps[mod] = {"installed": True, "version": ver}
        except ImportError:
            deps[mod] = {"installed": False, "version": "Not installed"}
    info["optional_dependencies"] = deps

    # Binary tools presence in PATH
    tools = {}
    for t in ["file", "readelf", "sha256sum", "objdump", "strings"]:
        tools[t] = shutil.which(t) is not None
    info["system_tools"] = tools

    return info

def print_device_info() -> None:
    """Prints formatted device and environment table."""
    info = get_environment_info()
    styler.print_banner()

    headers = ["Component", "Value"]
    rows = [
        ["Operating System", f"{info['os_name']} {info.get('distro', '')}"],
        ["Kernel Release", info["os_release"]],
        ["CPU Architecture", f"{info['architecture']} ({'64-bit' if info['is_64bit'] else '32-bit'}, {info['byteorder']}-endian)"],
        ["Processor Model", info["processor"]],
        ["Python Runtime", f"{info['python_version']} ({info['python_executable']})"],
        ["Working Directory", info["working_directory"]],
    ]
    styler.print_table("Host Device & Runtime Environment", headers, rows)

    dep_headers = ["Package / Module", "Status", "Version / Note"]
    dep_rows = []
    for k, v in info["optional_dependencies"].items():
        status = styler.badge("PASS") if v["installed"] else styler.badge("INFO")
        dep_rows.append([k, status, v["version"]])
    styler.print_table("Optional Python Dependencies", dep_headers, dep_rows)

    tool_headers = ["System Utility", "Status", "Description"]
    tool_rows = []
    for t, found in info["system_tools"].items():
        st = styler.badge("PASS") if found else styler.badge("INFO")
        tool_rows.append([t, st, "Available in PATH" if found else "Not found (Toolkit uses native fallback)"])
    styler.print_table("System Diagnostics Utilities", tool_headers, tool_rows)
