# Security and Responsible Use Policy

## Scope & Intent

**RogueByte RBRT Toolkit V2** is intended solely for authorized repair, hardware diagnostics, and digital forensic analysis of user-owned or explicitly authorized equipment and binary files.

## Responsible Engineering Principles

1. **Zero Telemetry**: RBRT Toolkit does not collect, transmit, or phone-home any usage data, IP addresses, filenames, hashes, or machine identifiers.
2. **Offline-First**: All analytical operations run purely locally. No cloud endpoints, remote authentication, or external API keys are required.
3. **No Flashing or Destructive Hardware Modification**: RBRT does not perform unsolicited SPI, NOR, or NAND flash writing. UART operations default to strictly read-only listening.
4. **No Code Execution During Analysis**: Binary, ELF, and PUP inspectors parse data strictly as inert structured byte streams. Input files are never dynamically executed.
5. **No Proprietary Key Distribution**: RBRT does not distribute or reverse-engineer proprietary decryption keys or copyrighted intellectual property.
6. **Path Safety**: All output report paths are validated to prevent directory traversal or accidental overwrites.

## Vulnerability Reporting

If you identify a security issue, vulnerability, or parser crash issue in RBRT Toolkit V2, please notify our team directly:

- **Security Contact**: `contact@roguebyte.online`
- **help**: help@roguebyte.online
- **business Contact**: business@roguebyte.online`
- **PGP/Key Verification**: Available on request via https://roguebyte.online
- **Response SLA**: Initial triage within 48 hours.

Please do not open public GitHub issues for unpatched security vulnerabilities.
