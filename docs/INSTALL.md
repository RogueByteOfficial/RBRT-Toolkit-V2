# Installation Guide — RogueByte RBRT Toolkit V2

Complete installation, dependency configuration, and verification procedures for Ubuntu, Debian, Kali, WSL2, and Windows environments.

---

## 1. System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, Kali Linux), WSL2, or Windows 10/11
- **Python**: Version 3.10 or higher (Python 3.11+ recommended)
- **Disk Space**: ~50 MB for core installation; 2 GB+ recommended for analyzing large firmware dumps
- **RAM**: Minimal (~30 MB runtime). All binary comparisons run in streaming 64 KB chunks.

---

## 2. Ubuntu / Debian / Kali / WSL2 Installation

### Step 1: Install System Packages
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git binutils file
```

### Step 2: Clone the Repository
```bash
# Replace YOUR_REPOSITORY_URL with the actual clone target
git clone https://github.com/RogueByteOfficial/RBRT-Toolkit-V2.git RBRT-Toolkit-V2
cd RBRT-Toolkit-V2
```

### Step 3: Create & Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 4: Upgrade Pip & Install RBRT
```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Step 5: Verify Installation
```bash
rbrt --version
rbrt doctor
```

---

## 3. Serial Port (UART) Permissions on Linux

To access USB-UART serial adapters without root (`sudo`):

```bash
# Add current user to dialout group (Ubuntu/Debian)
sudo usermod -aG dialout $USER

# On Arch / Manjaro / Fedora (if applicable):
# sudo usermod -aG uucp $USER

# Log out and log back in, or activate group in current shell:
newgrp dialout

# Verify group membership:
groups | grep -E "dialout|uucp"
```

Never run the entire toolkit as root merely to access a serial device.

---

## 4. Windows 10/11 Installation (PowerShell)

```powershell
# 1. Ensure Python 3.10+ is installed from python.org or Windows Terminal
python --version

# 2. Clone repository
git clone https://github.com/RogueByteOfficial/RBRT-Toolkit-V2.git RBRT-Toolkit-V2
cd RBRT-Toolkit-V2

# 3. Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 4. Install dependencies
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

# 5. Verify
rbrt --help
rbrt doctor
```

---

## 5. Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove installation directory
cd ..
rm -rf RBRT-Toolkit-V2
```
