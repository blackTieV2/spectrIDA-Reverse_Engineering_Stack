"""PE (Windows DLL/EXE) — idalib loads these natively, so this handler is pure
header parsing: section table + image base, so the generic shard-zeroing in
base.py has something to work with. No decompression, no post_open.

The COFF machine field is authoritative for arch — we hand it down as the
PreparedImage hint so a 32-bit PE never gets its bytes fed to a 64-bit
Capstone decoder (the shard_worker's IDA-procname fallback can't tell
"metapc" 32-bit from 64-bit on its own without an is_64bit() check)."""
from __future__ import annotations

import struct

from spectrida.analysis.formats.base import FormatHandler, PreparedImage, Section

_DOS_MAGIC = b"MZ"
_PE_SIG = b"PE\x00\x00"

# COFF machine field -> scanner arch hint (mirrors elf.py's _ARCH_HINTS)
_MACHINE_ARCH = {
    0x8664: "x86_64",   # IMAGE_FILE_MACHINE_AMD64
    0x014C: "x86",      # IMAGE_FILE_MACHINE_I386
    0xAA64: "arm64",    # ARM64 PE (Windows on ARM)
    0x01C0: "arm32",    # ARM little-endian
    0x01C4: "arm32",    # ARMv7 Thumb-2 little-endian
}


class PEHandler(FormatHandler):
    name = "PE"

    @staticmethod
    def sniff(header: bytes, path: str) -> bool:
        if len(header) < 0x40 or header[:2] != _DOS_MAGIC:
            return False
        pe_off = struct.unpack_from("<I", header, 0x3C)[0]
        return header[pe_off:pe_off + 4] == _PE_SIG

    def prepare(self, path: str, workdir: str) -> PreparedImage:
        return PreparedImage(
            binary_path=path,
            image_base=_image_base(path)[0],
            sections=_pe_sections(path),
            arch=_image_base(path)[1],
        )


def _image_base(path: str) -> tuple[int, str | None]:
    """Return (image_base, arch_hint). arch_hint comes from the COFF machine
    field; None for a machine type we don't map (scanner falls back to IDA's
    own detection in shard_worker)."""
    with open(path, "rb") as f:
        h = f.read(0x1000)
    pe_off = struct.unpack_from("<I", h, 0x3C)[0]
    machine = struct.unpack_from("<H", h, pe_off + 4)[0]
    is64 = machine in (0x8664, 0xAA64)
    ibase_off = pe_off + 24 + (24 if is64 else 28)
    fmt = "<Q" if is64 else "<I"
    return struct.unpack_from(fmt, h, ibase_off)[0], _MACHINE_ARCH.get(machine)


def _pe_sections(path: str) -> list[Section]:
    with open(path, "rb") as f:
        h = f.read(0x1000)
    pe_off = struct.unpack_from("<I", h, 0x3C)[0]
    num_sects = struct.unpack_from("<H", h, pe_off + 6)[0]
    opt_sz = struct.unpack_from("<H", h, pe_off + 20)[0]
    sect_off = pe_off + 24 + opt_sz
    sections = []
    for i in range(num_sects):
        o = sect_off + i * 40
        name = h[o:o + 8].rstrip(b"\x00").decode("ascii", errors="replace")
        vsize = struct.unpack_from("<I", h, o + 8)[0]
        vaddr = struct.unpack_from("<I", h, o + 12)[0]
        raw_size = struct.unpack_from("<I", h, o + 16)[0]
        raw_off = struct.unpack_from("<I", h, o + 20)[0]
        flags = struct.unpack_from("<I", h, o + 36)[0]
        is_code = bool(flags & 0x20)  # IMAGE_SCN_CNT_CODE
        sections.append(Section(name=name, va=vaddr, raw_off=raw_off, raw_size=raw_size, vsize=vsize, is_code=is_code))
    return sections


HANDLER = PEHandler()
