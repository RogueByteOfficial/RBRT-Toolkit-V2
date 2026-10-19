# UART Hardware Connection & Electrical Safety Guide

> **Important**: This guide is for certified repair technicians and engineers conducting hardware diagnostics on authorized equipment.

---

## 1. Electrical Levels & Voltage Hazard

Modern console architectures (such as PlayStation 4 Southbridge/Syscon and PlayStation 5 APU/Southbridge test pads) operate strictly at low-voltage CMOS logic:

- **Syscon / Southbridge UART**: Typically **3.3V** or **1.8V logic**.
- **Legacy PC RS-232**: Operates at **±12V** (Will instantaneously destroy components).
- **Generic 5V USB-TTL Cables**: Operates at **5.0V** (Will cause catastrophic breakdown of 1.8V/3.3V I/O transceivers).

### Mandatory Hardware Requirements
1. **Multi-voltage USB-UART Adapter**: Use a genuine FTDI (FT232RL) with physical 3.3V/1.8V jumper, or Silicon Labs CP2102 with verified 3.3V logic level.
2. **Logic Level Shifter**: If diagnosing 1.8V lines with a 3.3V adapter, insert a bidirectional logic level shifter (such as TXS0108E or BSS138).
3. **Common Ground (GND)**: Always establish the ground reference before connecting TX/RX lines or applying power.

---

## 2. PS4 / PS5 Board Revisions & Pinout Notice

Console motherboard revisions differ substantially between models:

| Generation | Example Board Models | Logic Level | Default Baud | Diagnostic Interface |
| :--- | :--- | :---: | :---: | :--- |
| **PS4 Fat** | SAA-001, SAB-001 | 3.3V | 115200 | Southbridge (CXD90025G) |
| **PS4 Slim** | SAD-001, SAE-001 | 3.3V | 115200 | Southbridge (CXD90046G) |
| **PS4 Pro** | NVA-001, NVB-001 | 3.3V | 115200 | Southbridge / Syscon Pads |
| **PS5 Fat** | EDM-010, EDM-020 | 3.3V / 1.8V | 115200 | Syscon (R5F100PLA) Debug Port |
| **PS5 Slim** | EDM-030 | 3.3V / 1.8V | 115200 | Dedicated test point headers |

Do not assume a universal pinout. Always verify against specific schematics for your board revision.

---

## 3. Safe Diagnostic Protocol

1. **Read-Only First**: Never inject serial TX data into an unverified board. Keep the host TX disconnected until you observe clean RX bootloader output.
2. **Cable Length**: Keep fly-wires under 15 cm (6 inches) to avoid RF ringing, baud distortion, and induced noise.
3. **Software Configuration**:
   - Baud Rate: `115200`
   - Data Bits: `8`
   - Parity: `None`
   - Stop Bits: `1`
   - Flow Control: `None`

---

## 4. Testing with Mock Backend (No Hardware Required)

You can verify your logging pipelines without any physical console or USB adapter:

```bash
rbrt uart log --port MOCK --baud 115200 --output test_boot.log --mock --duration 2.0
```
This streams simulated Southbridge initialization events directly into your log.
