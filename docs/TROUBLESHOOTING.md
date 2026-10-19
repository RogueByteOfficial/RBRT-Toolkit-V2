# Troubleshooting Guide — RogueByte RBRT Toolkit V2

## Common Issues & Solutions

### 1. Permission Denied on `/dev/ttyUSB0` or `/dev/ttyACM0`
**Cause**: Linux user account does not belong to the `dialout` or `uucp` group.  
**Fix**:
```bash
sudo usermod -aG dialout $USER
newgrp dialout
```
*Never run RBRT under `sudo` to bypass serial permissions.*

---

### 2. "ModuleNotFoundError: No module named 'serial'"
**Cause**: `pyserial` is not installed in the active Python environment.  
**Fix**:
```bash
pip install pyserial
# Or install all optional extensions:
pip install -e ".[full]"
```

---

### 3. File Comparison Shows 100% Divergence
**Cause**: Files are encrypted or compressed with different IVs/keys, or an offset shift exists at the very beginning of the dump.  
**Diagnostic**: Run `rbrt bin inspect` on both files to compare entropy and format hints.

---

### 4. `rbrt` Command Not Found After Installation
**Cause**: The virtual environment `.venv/bin` is not in your current `$PATH`.  
**Fix**:
```bash
source .venv/bin/activate
# Or invoke directly:
python -m rbrt doctor
```
