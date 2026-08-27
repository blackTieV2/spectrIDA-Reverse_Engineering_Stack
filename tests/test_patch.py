"""Tests for the patch safety contract (tp-2026-08-25-003 Part A).

No idalib in the sandbox — IDAHandle is faked with an in-memory byte store,
which is exactly what the worker protocol hides anyway.
"""
from __future__ import annotations

import pytest

from spectrida.core import patchlog
from spectrida.core.ida import revert_patch, verified_patch


class FakeIDA:
    """In-memory stand-in for IDAHandle: .call interface + .i64 path."""

    def __init__(self, store: dict[int, int], i64: str, mode: str = "64"):
        self.store = store
        self.i64 = i64
        self.mode = mode
        self.fail_patch = False

    async def call(self, cmd: str, **args):
        if cmd == "bits":
            return self.mode
        if cmd == "get_bytes":
            addr = int(args["address"], 16)
            size = int(args["size"])
            try:
                return bytes(self.store[addr + i] for i in range(size)).hex()
            except KeyError:
                return None
        if cmd == "patch":
            if self.fail_patch:
                return False
            addr = int(args["address"], 16)
            data = bytes.fromhex(args["hex"])
            for i, b in enumerate(data):
                self.store[addr + i] = b
            return True
        raise ValueError(cmd)


def _store() -> dict[int, int]:
    # 0x1000: push ebp; mov ebp,esp; sub esp,8  (32-bit-friendly bytes)
    data = bytes.fromhex("558bec83ec08") + b"\x90" * 10
    return {0x1000 + i: b for i, b in enumerate(data)}


# ── journal module ──────────────────────────────────────────────────────────

def test_journal_write_read_revert(tmp_path) -> None:
    i64 = tmp_path / "target.i64"
    i64.touch()
    e = patchlog.append_entry(i64, addr=0x1000, old_bytes=b"\x55\x8b",
                              new_bytes=b"\x90\x90", mode="32")
    entries = patchlog.list_entries(i64)
    assert len(entries) == 1 and entries[0]["id"] == e["id"]
    assert entries[0]["reverted"] is False
    patchlog.mark_reverted(i64, e["id"])
    assert patchlog.list_entries(i64)[0]["reverted"] is True
    assert patchlog.find_entry(i64, e["id"])["addr"] == 0x1000
    assert patchlog.find_entry(i64, "nope") is None


def test_journal_empty_and_torn(tmp_path) -> None:
    i64 = tmp_path / "x.i64"
    assert patchlog.list_entries(i64) == []
    i64.touch()
    patchlog.append_entry(i64, addr=1, old_bytes=b"a", new_bytes=b"b", mode="64")
    # simulate a torn last line
    with patchlog.journal_path(i64).open("a") as f:
        f.write('{"id": "broken')
    entries = patchlog.list_entries(i64)
    assert len(entries) == 1


def test_decode_check_modes() -> None:
    # 0x06 = push es: VALID in 32-bit, INVALID in 64-bit (the fork's trick)
    r32 = patchlog.decode_check(b"\x06", "32")
    r64 = patchlog.decode_check(b"\x06", "64")
    assert r32["decode_ok"] is True and r32["decoded"][0].startswith("push")
    assert r64["decode_ok"] is False
    assert r32["mode"] == "32" and r64["mode"] == "64"


# ── verified_patch orchestration ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_patch_journal_before_write_and_readback(tmp_path) -> None:
    i64 = tmp_path / "t.i64"
    i64.touch()
    ida = FakeIDA(_store(), str(i64), mode="32")
    res = await verified_patch(ida, 0x1003, bytes.fromhex("31c0"))  # xor eax,eax
    assert res["verified"] is True
    assert res["mode"] == "32"
    assert res["decode_ok"] is True
    assert "xor eax, eax" in res["decoded"][0]
    # journal entry exists and matches
    e = patchlog.list_entries(i64)[0]
    assert e["old_bytes"] == "83ec" and e["new_bytes"] == "31c0"
    # store actually changed
    assert ida.store[0x1003] == 0x31 and ida.store[0x1004] == 0xC0


@pytest.mark.asyncio
async def test_patch_unmapped_raises_and_no_write(tmp_path) -> None:
    i64 = tmp_path / "t.i64"
    i64.touch()
    ida = FakeIDA(_store(), str(i64))
    with pytest.raises(ValueError, match="not mapped"):
        await verified_patch(ida, 0x9000, b"\x90")
    assert patchlog.list_entries(i64) == []  # never journaled


@pytest.mark.asyncio
async def test_revert_restores_exact_bytes(tmp_path) -> None:
    i64 = tmp_path / "t.i64"
    i64.touch()
    ida = FakeIDA(_store(), str(i64), mode="32")
    res = await verified_patch(ida, 0x1003, bytes.fromhex("31c0"))
    assert ida.store[0x1003] == 0x31
    out = await revert_patch(ida, res["entry"]["id"])
    assert out["reverted"] is True
    assert ida.store[0x1003] == 0x83 and ida.store[0x1004] == 0xEC
    # second revert is a no-op note, not an error
    again = await revert_patch(ida, res["entry"]["id"])
    assert again.get("note") == "already reverted"


@pytest.mark.asyncio
async def test_revert_unknown_id_raises(tmp_path) -> None:
    i64 = tmp_path / "t.i64"
    i64.touch()
    ida = FakeIDA(_store(), str(i64))
    with pytest.raises(ValueError, match="no patch entry"):
        await revert_patch(ida, "missing")


class FlakyReadIDA(FakeIDA):
    """Patch lands but read-back returns garbage — the contract must auto-revert."""

    async def call(self, cmd: str, **args):
        if cmd == "get_bytes" and getattr(self, "_patched_once", False):
            return "deadbeef" + "00" * (int(args["size"]) - 2)
        if cmd == "patch":
            self._patched_once = True
        return await super().call(cmd, **args)


@pytest.mark.asyncio
async def test_readback_mismatch_auto_reverts(tmp_path) -> None:
    i64 = tmp_path / "t.i64"
    i64.touch()
    ida = FlakyReadIDA(_store(), str(i64), mode="32")
    with pytest.raises(RuntimeError, match="read-back mismatch"):
        await verified_patch(ida, 0x1003, bytes.fromhex("31c0"))
    # journal entry exists and is flagged reverted
    entries = patchlog.list_entries(i64)
    assert len(entries) == 1 and entries[0]["reverted"] is True


def test_worker_patch_uses_patch_byte_not_void_wrapper():
    """Regression for the live failure of 2026-08-27: ida_bytes.patch_bytes
    returns None (void SWIG wrapper); bool(None) reported 'refused' while the
    patch actually landed in the .i64. The worker must use patch_byte, whose
    return value is a real success flag."""
    from spectrida.core import ida as ida_mod
    assert "patch_byte(" in ida_mod._WORKER
    patch_branch = ida_mod._WORKER.split('cmd == "patch"')[1].split("elif")[0]
    assert "patch_bytes(" not in patch_branch
