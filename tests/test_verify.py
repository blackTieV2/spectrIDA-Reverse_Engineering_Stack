"""Tests for tp-2026-08-27-005: real verify_decompilation (differential oracle).

Hand-assembled byte pairs and a faked live db — no IDA, no Ollama.
End-to-end gcc tests skip cleanly when the host has no toolchain
(degradation is the designed behaviour, design packet D4).
"""
from __future__ import annotations

import asyncio
import shutil

import pytest

from spectrida.verify.oracle import (
    compare_emulations,
    compile_c_to_shared,
    emulate_function,
    extract_function_bytes,
    verify_function,
)

# mov eax, 5 ; ret
X86_MOV5_RET = bytes.fromhex("b805000000c3")
# mov eax, ecx ; ret          (x64: first arg in ecx)
X64_ECHO_ARG = bytes.fromhex("89c8c3")
# mov eax, [esp+4] ; ret      (cdecl: first arg on stack)
X86_ECHO_ARG = bytes.fromhex("8b442404c3")
# mov eax, [esp+4] ; add eax, [esp+8] ; ret
X86_ADD_ARGS = bytes.fromhex("8b44240403442408c3")

HAS_GCC = bool(shutil.which("gcc") or shutil.which("g++"))
HAS_OBJDUMP = bool(shutil.which("objdump"))


def run(coro):
    return asyncio.run(coro)


# ── emulation: 64-bit ────────────────────────────────────────────────────────

def test_emulate_64bit_const_return():
    r = emulate_function(X86_MOV5_RET, bits=64)
    assert not r.error
    assert r.return_value == 5


def test_emulate_64bit_register_arg_echo():
    r = emulate_function(X64_ECHO_ARG, args=[42], bits=64)
    assert not r.error
    assert r.return_value == 42


# ── emulation: 32-bit (dec-2026-08-27-005 D1 — the live UAT target is x86) ──

def test_emulate_32bit_const_return():
    r = emulate_function(X86_MOV5_RET, bits=32)
    assert not r.error
    assert r.return_value == 5


def test_emulate_32bit_stack_arg_echo():
    r = emulate_function(X86_ECHO_ARG, args=[7], bits=32)
    assert not r.error
    assert r.return_value == 7


def test_emulate_32bit_two_stack_args():
    r = emulate_function(X86_ADD_ARGS, args=[3, 4], bits=32)
    assert not r.error
    assert r.return_value == 7


# ── comparison oracle ─────────────────────────────────────────────────────────

def test_compare_identical_is_equivalent():
    a = emulate_function(X86_MOV5_RET, bits=64)
    v = compare_emulations(a, a)
    assert v.equivalent
    assert v.return_match


def test_compare_mismatch_detected():
    a = emulate_function(X86_MOV5_RET, bits=64)
    b = emulate_function(bytes.fromhex("b809000000c3"), bits=64)  # mov eax,9
    v = compare_emulations(a, b, tolerance=0.0)
    assert not v.equivalent
    assert not v.return_match


def test_compare_emulation_error_propagates():
    from spectrida.verify.oracle import EmulationResult
    v = compare_emulations(EmulationResult(error="boom"),
                           EmulationResult(return_value=1))
    assert not v.equivalent
    assert "boom" in v.reason


# ── compile/extract (host toolchain; skip without) ───────────────────────────

@pytest.mark.skipif(not (HAS_GCC and HAS_OBJDUMP), reason="no host toolchain")
def test_extract_first_function_fallback(tmp_path):
    out = str(tmp_path / "f.dll")
    r = compile_c_to_shared("int target_fn(int a) { return a + 1; }", out)
    assert r["ok"], r.get("error")
    x = extract_function_bytes(out, "")  # no name → first label
    assert x["ok"], x.get("error")
    assert x["size"] > 0


@pytest.mark.skipif(not (HAS_GCC and HAS_OBJDUMP), reason="no host toolchain")
def test_verify_function_equivalent_e2e(tmp_path):
    src = "int f(int a) { return a * 2 + 1; }"
    out = str(tmp_path / "f.dll")
    assert compile_c_to_shared(src, out)["ok"]
    original = bytes.fromhex(extract_function_bytes(out, "")["bytes"])
    v = verify_function(original, src, args=[10], bits=64)
    assert v.equivalent, v.reason


@pytest.mark.skipif(not (HAS_GCC and HAS_OBJDUMP), reason="no host toolchain")
def test_verify_function_detects_mismatch_e2e(tmp_path):
    out = str(tmp_path / "f.dll")
    assert compile_c_to_shared("int f(int a) { return a + 1; }", out)["ok"]
    original = bytes.fromhex(extract_function_bytes(out, "")["bytes"])
    # recompiled candidate behaves differently (a*5 vs a+1, far beyond tolerance)
    v = verify_function(original, "int f(int a) { return a * 5; }",
                        args=[10], bits=64)
    assert not v.equivalent


def test_verify_function_no_toolchain_is_data(monkeypatch):
    monkeypatch.setattr("spectrida.verify.oracle._find_tool", lambda name: "")
    v = verify_function(X86_MOV5_RET, "int f(){return 5;}")
    assert not v.equivalent
    assert "gcc not found" in v.reason


# ── MCP tool wiring (faked live db) ──────────────────────────────────────────

class FakeDB:
    def __init__(self, *, info={"start": 0x1000, "end": 0x1006},
                 data=X86_MOV5_RET, bits="64",
                 pseudo="int f() { return 5; }"):
        self._info, self._data, self._bits, self._pseudo = info, data, bits, pseudo

    async def info(self, addr):
        return self._info

    async def read_bytes(self, addr, size):
        return self._data

    async def bits(self):
        return self._bits

    async def decompile(self, addr):
        return self._pseudo


def _patch_db(monkeypatch, db):
    import spectrida.mcp_server as srv

    async def fake_live_db(binary):
        return db
    monkeypatch.setattr(srv, "_live_db", fake_live_db)
    return srv


def test_tool_no_function_at_address(monkeypatch):
    srv = _patch_db(monkeypatch, FakeDB(info=None))
    r = run(srv.verify_decompilation("bin", "0x1000", "int f(){return 5;}"))
    assert r["verified"] is False
    assert r["status"] == "inconclusive"
    assert "no function" in r["reason"]


def test_tool_oversized_function_degrades(monkeypatch):
    db = FakeDB(info={"start": 0x1000, "end": 0x1000 + 0x20000})
    srv = _patch_db(monkeypatch, db)
    r = run(srv.verify_decompilation("bin", "0x1000", "int f(){return 5;}"))
    assert r["verified"] is False
    assert r["status"] == "inconclusive"
    assert "size" in r["reason"]


def test_tool_unreadable_bytes_degrades(monkeypatch):
    srv = _patch_db(monkeypatch, FakeDB(data=None))
    r = run(srv.verify_decompilation("bin", "0x1000", "int f(){return 5;}"))
    assert r["verified"] is False
    assert r["status"] == "inconclusive"


def test_tool_no_toolchain_degrades(monkeypatch):
    monkeypatch.setattr("spectrida.verify.oracle._find_tool", lambda name: "")
    srv = _patch_db(monkeypatch, FakeDB())
    r = run(srv.verify_decompilation("bin", "0x1000", "int f(){return 5;}"))
    assert r["verified"] is False
    assert r["status"] == "no_toolchain"
    # planner contract: only verified:true upgrades; everything else queues
    assert r["status"] != "ready_for_verification"  # stub shape is gone


@pytest.mark.skipif(not (HAS_GCC and HAS_OBJDUMP), reason="no host toolchain")
def test_tool_verified_path(monkeypatch):
    srv = _patch_db(monkeypatch, FakeDB())
    r = run(srv.verify_decompilation("bin", "0x1000", "int f() { return 5; }"))
    assert r["verified"] is True
    assert r["status"] == "verified"


@pytest.mark.skipif(not (HAS_GCC and HAS_OBJDUMP), reason="no host toolchain")
def test_tool_mismatch_path(monkeypatch):
    srv = _patch_db(monkeypatch, FakeDB())
    r = run(srv.verify_decompilation("bin", "0x1000",
                                     "int f() { return 5000; }"))
    assert r["verified"] is False
    assert r["status"] == "mismatch"
    assert r["details"]



# ── objdump resolution regression (live BlackTie 2026-09-01: SPECTRIDA_GCC was
# honoured but extract_function_bytes shelled out to a bare "objdump" on PATH —
# the env override existed and was never used) ────────────────────────────────

def test_extract_resolves_objdump_via_find_tool():
    import inspect
    from spectrida.verify import oracle
    src = inspect.getsource(oracle.extract_function_bytes)
    assert '_find_tool("objdump")' in src
    assert 'os.popen("objdump' not in src  # bare-PATH fallback must stay dead


def test_extract_missing_objdump_is_data(monkeypatch):
    monkeypatch.setattr("spectrida.verify.oracle._find_tool", lambda name: "")
    r = extract_function_bytes("whatever.dll", "")
    assert r["ok"] is False
    assert "objdump not found" in r["error"]
