# PlayStation Update Package (PUP) Support Matrix

## 1. Overview of the PUP Container Format

PlayStation Update Packages (PUP) wrap system software, recovery images, and secondary bootloaders within a proprietary Sony Computer Entertainment (`SCE\0`) container.

### Header Specification (Big-Endian)
- `0x00` - Magic: `0x53434500` (`SCE\0`)
- `0x04` - Package Version (uint32)
- `0x08` - Image Version (uint32)
- `0x0C` - Package Flags (uint32)
- `0x10` - Number of File Entries (uint64)
- `0x18` - Header Length (uint64)
- `0x20` - Package Length (uint64)

Following the header is an entry table defining sub-payload IDs, byte offsets, lengths, and cryptographic flags.

---

## 2. Compatibility & Capability Matrix

| Container Version / Platform | Header Validation | Table of Contents | Encrypted Block Detection | Binary Comparison | Payload Decryption |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **PS4 Retail Update (1.00 - 11.xx)** | Supported | Supported | Supported | Supported | **Unsupported (No Keys)** |
| **PS4 Recovery PUP** | Supported | Supported | Supported | Supported | **Unsupported (No Keys)** |
| **PS5 System Software (1.00+)** | Supported | Supported | Supported | Supported | **Unsupported (No Keys)** |
| **Corrupted / Truncated PUP** | Detected & Flagged | Detected & Flagged | N/A | Supported | N/A |

---

## 3. Responsible Engineering Policy Regarding Encryption

- RBRT Toolkit V2 **does not bundle proprietary Sony private keys or per-console decryption secrets**.
- We do not pretend to extract or decrypt retail firmware without legitimate keys.
- When `rbrt pup inspect` runs, it accurately reports the valid outer container structure and transparently notifies the user that internal payloads are encrypted.
