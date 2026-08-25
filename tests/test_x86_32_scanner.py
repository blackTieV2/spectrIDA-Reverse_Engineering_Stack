"""32-bit x86 (CS_MODE_32) scanner support.

Regression: the Capstone pass used to be hardcoded CS_MODE_64, so a 32-bit
PE's bytes were decoded by the 64-bit decoder — silently wrong instruction
boundaries/operands. `arch="x86"` must route to the 32-bit decoder, and the
PE handler must supply that hint from the COFF machine field (IMAGE_FILE_
MACHINE_I386 = 0x14C) instead of leaving it to IDA's procname, which can't
distinguish 32- from 64-bit "metapc" on its own.
"""
from __future__ import annotations

import struct

import pytest

pytest.importorskip("capstone")

from spectrida.analysis.formats.pe import PEHandler
from spectrida.analysis.ida_gpu_accel.capstone_scanner import _scan_shard_x86, scan_shard

BASE = 0x1000

# push ebp ; mov ebp, esp ; push es ; pop ebp ; ret
# 0x06 (push es) is VALID in 32-bit and INVALID in 64-bit — it makes the
# decode mode observable: mode32 reaches the final RET, mode64 stalls early.
_FUNC32 = bytes([0x55, 0x8B, 0xEC, 0x06, 0x5D, 0xC3])


def test_scan_shard_arch_x86_uses_32bit_decoder():
    result = scan_shard(_FUNC32, BASE, BASE, BASE + len(_FUNC32),
                        arch="x86", entry_points=[BASE])
    assert len(result.funcs) == 1
    fn = result.funcs[0]
    assert fn.ea == BASE
    # mode32 decodes all six bytes (through the RET); mode64 would stop at 0x06
    assert fn.size == len(_FUNC32)


def test_scan_shard_mode64_stalls_on_32bit_only_instruction():
    # Same bytes through the 64-bit decoder: 0x06 is invalid there, so the
    # walk never reaches the trailing RET. This pins the behavioural
    # difference the mode32 fix is based on.
    result = _scan_shard_x86(_FUNC32, BASE, BASE, BASE + len(_FUNC32),
                             [BASE], mode32=False)
    assert len(result.funcs) == 1
    assert result.funcs[0].size < len(_FUNC32)


def test_scan_shard_x86_finds_call_target():
    # main: push ebp; mov ebp,esp; call callee; xor eax,eax; pop ebp; ret
    # callee: push ebp; mov ebp,esp; xor eax,eax; pop ebp; ret
    main = bytes([0x55, 0x8B, 0xEC]) + b"\xE8" + struct.pack("<i", 0x07) + \
           bytes([0x31, 0xC0, 0x5D, 0xC3])
    pad = b"\xCC" * 3
    callee = bytes([0x55, 0x8B, 0xEC, 0x31, 0xC0, 0x5D, 0xC3])
    data = main + pad + callee
    result = scan_shard(data, BASE, BASE, BASE + len(data),
                        arch="x86", entry_points=[BASE])
    eas = {f.ea for f in result.funcs}
    assert BASE in eas
    assert BASE + len(main) + len(pad) in eas  # the call target


def _make_pe32(tmp_path, machine=0x14C):
    """Minimal PE32 header: DOS stub + PE sig + COFF + optional header + one
    .text section. Only the fields the handler reads are populated."""
    buf = bytearray(0x400)
    buf[0:2] = b"MZ"
    struct.pack_into("<I", buf, 0x3C, 0x80)          # e_lfanew
    buf[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<H", buf, 0x84, machine)        # Machine
    struct.pack_into("<H", buf, 0x86, 1)              # NumberOfSections
    struct.pack_into("<H", buf, 0x94, 0xE0)           # SizeOfOptionalHeader
    struct.pack_into("<H", buf, 0x98, 0x010B)         # PE32 magic
    struct.pack_into("<I", buf, 0x98 + 28, 0x400000)  # ImageBase (PE32)
    sect = 0x98 + 0xE0
    buf[sect:sect + 8] = b".text\x00\x00\x00"
    struct.pack_into("<I", buf, sect + 8, 0x200)      # VirtualSize
    struct.pack_into("<I", buf, sect + 12, 0x1000)    # VirtualAddress
    struct.pack_into("<I", buf, sect + 16, 0x200)     # SizeOfRawData
    struct.pack_into("<I", buf, sect + 20, 0x200)     # PointerToRawData
    struct.pack_into("<I", buf, sect + 36, 0x60000020)  # CODE|EXECUTE|READ
    p = tmp_path / "test32.exe"
    p.write_bytes(bytes(buf))
    return p


def test_pe_handler_hints_x86_for_i386(tmp_path):
    p = _make_pe32(tmp_path, machine=0x14C)
    image = PEHandler().prepare(str(p), workdir=str(tmp_path))
    assert image.arch == "x86"
    assert image.image_base == 0x400000


def test_pe_handler_hints_x86_64_for_amd64(tmp_path):
    buf = bytearray(_make_pe32(tmp_path).read_bytes())
    struct.pack_into("<H", buf, 0x84, 0x8664)         # Machine = AMD64
    struct.pack_into("<H", buf, 0x98, 0x020B)         # PE32+ magic
    struct.pack_into("<Q", buf, 0x98 + 24, 0x140000000)  # ImageBase (PE32+)
    p = tmp_path / "test64.exe"
    p.write_bytes(bytes(buf))
    image = PEHandler().prepare(str(p), workdir=str(tmp_path))
    assert image.arch == "x86_64"
    assert image.image_base == 0x140000000
