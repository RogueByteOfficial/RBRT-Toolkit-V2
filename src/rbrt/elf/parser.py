"""ELF (Executable and Linkable Format) 32/64-bit inspection, symbol parsing, and diff engine.
Pure-Python structural parser with transparent pyelftools enhancement.
"""

import struct
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple

from rbrt.utils.hashing import compute_file_sha256

# Try importing pyelftools
try:
    from elftools.elf.elffile import ELFFile as PyELFFile
    _HAS_PYELFTOOLS = True
except ImportError:
    _HAS_PYELFTOOLS = False


# ELF Constants
ELF_MAGIC = b"\x7fELF"

ELF_CLASSES = {
    1: "ELF32 (32-bit)",
    2: "ELF64 (64-bit)"
}

ELF_DATA_ENDIAN = {
    1: "Little-endian (2's complement, LSB)",
    2: "Big-endian (2's complement, MSB)"
}

ELF_TYPES = {
    0: "ET_NONE (No file type)",
    1: "ET_REL (Relocatable object file)",
    2: "ET_EXEC (Executable file)",
    3: "ET_DYN (Shared object / Dynamic library)",
    4: "ET_CORE (Core dump)"
}

ELF_MACHINES = {
    0x02: "SPARC",
    0x03: "x86 (Intel 80386)",
    0x08: "MIPS",
    0x14: "PowerPC",
    0x28: "ARM",
    0x32: "IA-64 (Intel Itanium)",
    0x3E: "x86-64 (AMD64 / Intel 64)",
    0xB7: "AArch64 (ARM 64-bit)",
    0xF3: "RISC-V",
}

SECTION_TYPES = {
    0: "SHT_NULL",
    1: "SHT_PROGBITS",
    2: "SHT_SYMTAB",
    3: "SHT_STRTAB",
    4: "SHT_RELA",
    5: "SHT_HASH",
    6: "SHT_DYNAMIC",
    7: "SHT_NOTE",
    8: "SHT_NOBITS",
    9: "SHT_REL",
    11: "SHT_DYNSYM",
}

SEGMENT_TYPES = {
    0: "PT_NULL",
    1: "PT_LOAD",
    2: "PT_DYNAMIC",
    3: "PT_INTERP",
    4: "PT_NOTE",
    5: "PT_SHLIB",
    6: "PT_PHDR",
    7: "PT_TLS",
    0x6474E550: "PT_GNU_EH_FRAME",
    0x6474E551: "PT_GNU_STACK",
    0x6474E552: "PT_GNU_RELRO",
}

@dataclass
class ELFSectionInfo:
    index: int
    name: str
    type_name: str
    flags: int
    addr: int
    offset: int
    size: int

@dataclass
class ELFSegmentInfo:
    index: int
    type_name: str
    flags: int
    offset: int
    vaddr: int
    filesz: int
    memsz: int

@dataclass
class ELFAnalysisResult:
    file_path: str
    file_name: str
    file_size: int
    sha256: str
    is_valid_elf: bool
    error: Optional[str]
    bitness: Optional[str]
    endianness: Optional[str]
    os_abi: Optional[str]
    object_type: Optional[str]
    machine_arch: Optional[str]
    entry_point: Optional[str]
    sections: List[ELFSectionInfo]
    segments: List[ELFSegmentInfo]
    symbols_count: int
    dynamic_libraries: List[str]
    is_stripped: bool
    structural_warnings: List[str]
    parser_used: str


class NativeELFParser:
    """Robust, pure-Python 32/64-bit ELF parser requiring zero external dependencies."""

    def __init__(self, file_path: Path):
        self.path = file_path
        self.size = file_path.stat().st_size
        self.warnings: List[str] = []

    def parse(self) -> ELFAnalysisResult:
        sha256 = compute_file_sha256(self.path)

        if self.size < 52:
            return ELFAnalysisResult(
                file_path=str(self.path),
                file_name=self.path.name,
                file_size=self.size,
                sha256=sha256,
                is_valid_elf=False,
                error=f"File too small for ELF header ({self.size} bytes).",
                bitness=None, endianness=None, os_abi=None, object_type=None,
                machine_arch=None, entry_point=None, sections=[], segments=[],
                symbols_count=0, dynamic_libraries=[], is_stripped=True,
                structural_warnings=["Truncated file before completing identification."],
                parser_used="native_struct"
            )

        with self.path.open("rb") as f:
            e_ident = f.read(16)

            if not e_ident.startswith(ELF_MAGIC):
                return ELFAnalysisResult(
                    file_path=str(self.path),
                    file_name=self.path.name,
                    file_size=self.size,
                    sha256=sha256,
                    is_valid_elf=False,
                    error="Magic number mismatch: Expected 0x7F 0x45 0x4C 0x46 (\\x7fELF).",
                    bitness=None, endianness=None, os_abi=None, object_type=None,
                    machine_arch=None, entry_point=None, sections=[], segments=[],
                    symbols_count=0, dynamic_libraries=[], is_stripped=True,
                    structural_warnings=["Not a recognized ELF binary."],
                    parser_used="native_struct"
                )

            ei_class = e_ident[4]
            ei_data = e_ident[5]
            ei_osabi = e_ident[7]

            bitness = ELF_CLASSES.get(ei_class, f"Unknown bitness ({ei_class})")
            endian = ELF_DATA_ENDIAN.get(ei_data, f"Unknown endianness ({ei_data})")
            endian_fmt = "<" if ei_data == 1 else ">"
            is_64 = (ei_class == 2)

            os_abi_names = {0: "System V / Generic", 3: "Linux", 9: "FreeBSD", 0x61: "ARM"}
            os_abi = os_abi_names.get(ei_osabi, f"ABI 0x{ei_osabi:02X}")

            # Read remaining header
            if is_64:
                header_data = f.read(48)  # 64-bit ELF header is 64 bytes total
                if len(header_data) < 48:
                    return self._create_truncated_result(sha256, bitness, endian, "ELF64 header truncated.")
                e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = struct.unpack(
                    f"{endian_fmt}HHIQQQIHHHHHH", header_data
                )
            else:
                header_data = f.read(36)  # 32-bit ELF header is 52 bytes total
                if len(header_data) < 36:
                    return self._create_truncated_result(sha256, bitness, endian, "ELF32 header truncated.")
                e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = struct.unpack(
                    f"{endian_fmt}HHIIIIIHHHHHH", header_data
                )

            obj_type = ELF_TYPES.get(e_type, f"Unknown (0x{e_type:04X})")
            machine = ELF_MACHINES.get(e_machine, f"Machine ID 0x{e_machine:04X}")

            # Parse Program Headers (Segments)
            segments: List[ELFSegmentInfo] = []
            if e_phoff > 0 and e_phnum > 0:
                if e_phoff + (e_phnum * e_phentsize) > self.size:
                    self.warnings.append("Program header table extends past end of file (truncated).")
                else:
                    f.seek(e_phoff)
                    for idx in range(e_phnum):
                        if is_64:
                            ph_data = f.read(56)
                            if len(ph_data) < 56:
                                break
                            p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack(f"{endian_fmt}IIQQQQQQ", ph_data)
                        else:
                            ph_data = f.read(32)
                            if len(ph_data) < 32:
                                break
                            p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack(f"{endian_fmt}IIIIIIII", ph_data)

                        segments.append(ELFSegmentInfo(
                            index=idx,
                            type_name=SEGMENT_TYPES.get(p_type, f"0x{p_type:08X}"),
                            flags=p_flags,
                            offset=p_offset,
                            vaddr=p_vaddr,
                            filesz=p_filesz,
                            memsz=p_memsz
                        ))

            # Parse Section Headers
            sections: List[ELFSectionInfo] = []
            raw_sh_records = []
            shstrtab_data = b""

            if e_shoff > 0 and e_shnum > 0:
                if e_shoff + (e_shnum * e_shentsize) > self.size:
                    self.warnings.append("Section header table extends past end of file (truncated).")
                else:
                    f.seek(e_shoff)
                    for idx in range(e_shnum):
                        if is_64:
                            sh_data = f.read(64)
                            if len(sh_data) < 64:
                                break
                            sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link, sh_info, sh_addralign, sh_entsize = struct.unpack(f"{endian_fmt}IIQQQQIIQQ", sh_data)
                        else:
                            sh_data = f.read(40)
                            if len(sh_data) < 40:
                                break
                            sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link, sh_info, sh_addralign, sh_entsize = struct.unpack(f"{endian_fmt}IIIIIIIIII", sh_data)

                        raw_sh_records.append((sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link))

                    # Read section string table if present
                    if 0 <= e_shstrndx < len(raw_sh_records):
                        str_rec = raw_sh_records[e_shstrndx]
                        if str_rec[4] + str_rec[5] <= self.size:
                            f.seek(str_rec[4])
                            shstrtab_data = f.read(str_rec[5])

            def get_sec_name(offset: int) -> str:
                if not shstrtab_data or offset >= len(shstrtab_data):
                    return f"sec_{offset}"
                end = shstrtab_data.find(b"\x00", offset)
                if end == -1:
                    end = len(shstrtab_data)
                return shstrtab_data[offset:end].decode("ascii", errors="replace")

            symtab_count = 0
            dyn_libs: List[str] = []

            for idx, r in enumerate(raw_sh_records):
                name = get_sec_name(r[0])
                type_name = SECTION_TYPES.get(r[1], f"0x{r[1]:08X}")
                sections.append(ELFSectionInfo(
                    index=idx,
                    name=name,
                    type_name=type_name,
                    flags=r[2],
                    addr=r[3],
                    offset=r[4],
                    size=r[5]
                ))

                if r[1] in (2, 11):  # SHT_SYMTAB or SHT_DYNSYM
                    # Estimate symbols count based on entry size
                    entsize = 24 if is_64 else 16
                    if entsize > 0 and r[5] > 0:
                        symtab_count += (r[5] // entsize)

            is_stripped = (symtab_count == 0) and not any(s.type_name == "SHT_SYMTAB" for s in sections)

            return ELFAnalysisResult(
                file_path=str(self.path),
                file_name=self.path.name,
                file_size=self.size,
                sha256=sha256,
                is_valid_elf=True,
                error=None,
                bitness=bitness,
                endianness=endian,
                os_abi=os_abi,
                object_type=obj_type,
                machine_arch=machine,
                entry_point=f"0x{e_entry:08X}",
                sections=sections,
                segments=segments,
                symbols_count=symtab_count,
                dynamic_libraries=dyn_libs,
                is_stripped=is_stripped,
                structural_warnings=self.warnings,
                parser_used="native_struct"
            )

    def _create_truncated_result(self, sha256: str, bitness: str, endian: str, err: str) -> ELFAnalysisResult:
        return ELFAnalysisResult(
            file_path=str(self.path),
            file_name=self.path.name,
            file_size=self.size,
            sha256=sha256,
            is_valid_elf=False,
            error=err,
            bitness=bitness,
            endianness=endian,
            os_abi=None,
            object_type=None,
            machine_arch=None,
            entry_point=None,
            sections=[],
            segments=[],
            symbols_count=0,
            dynamic_libraries=[],
            is_stripped=True,
            structural_warnings=["Header truncated before completion."],
            parser_used="native_struct"
        )


def analyze_elf_file(file_path: Path) -> ELFAnalysisResult:
    """Analyzes an ELF binary file with robust fallback."""
    parser = NativeELFParser(file_path)
    result = parser.parse()

    # Optional pyelftools enhancement if installed and valid
    if _HAS_PYELFTOOLS and result.is_valid_elf:
        try:
            with file_path.open("rb") as f:
                elffile = PyELFFile(f)
                # Check dynamic section for NEEDED tags
                dyn_sec = elffile.get_section_by_name(".dynamic")
                if dyn_sec:
                    for tag in dyn_sec.iter_tags():
                        if tag.entry.d_tag == "DT_NEEDED":
                            result.dynamic_libraries.append(tag.needed)
                result.parser_used = "pyelftools+native"
        except Exception:
            pass

    return result


def compare_elf_files(file_a: Path, file_b: Path) -> Dict[str, Any]:
    """Compares two ELF files at architecture, entry point, and section levels."""
    elf_a = analyze_elf_file(file_a)
    elf_b = analyze_elf_file(file_b)

    sec_names_a = {s.name: s for s in elf_a.sections}
    sec_names_b = {s.name: s for s in elf_b.sections}

    common_sections = sorted(list(set(sec_names_a.keys()) & set(sec_names_b.keys())))
    only_in_a = sorted(list(set(sec_names_a.keys()) - set(sec_names_b.keys())))
    only_in_b = sorted(list(set(sec_names_b.keys()) - set(sec_names_a.keys())))

    section_deltas = []
    for s_name in common_sections:
        sa = sec_names_a[s_name]
        sb = sec_names_b[s_name]
        if sa.size != sb.size or sa.addr != sb.addr:
            section_deltas.append({
                "section": s_name,
                "size_a": sa.size,
                "size_b": sb.size,
                "size_delta": sb.size - sa.size,
                "addr_a": f"0x{sa.addr:08X}",
                "addr_b": f"0x{sb.addr:08X}"
            })

    return {
        "file_a": str(file_a),
        "file_b": str(file_b),
        "arch_match": elf_a.machine_arch == elf_b.machine_arch,
        "arch_a": elf_a.machine_arch,
        "arch_b": elf_b.machine_arch,
        "entry_point_match": elf_a.entry_point == elf_b.entry_point,
        "entry_a": elf_a.entry_point,
        "entry_b": elf_b.entry_point,
        "sha256_match": elf_a.sha256 == elf_b.sha256,
        "common_sections_count": len(common_sections),
        "modified_sections_count": len(section_deltas),
        "sections_only_in_a": only_in_a,
        "sections_only_in_b": only_in_b,
        "modified_sections": section_deltas,
        "summary": (
            f"ELF Comparison: {len(section_deltas)} section(s) modified, "
            f"{len(only_in_a)} unique to A, {len(only_in_b)} unique to B."
        )
    }
