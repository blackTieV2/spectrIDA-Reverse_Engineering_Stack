"""Patch journal: append-only JSONL log of byte patches with revert support.

Safety contract (tp-2026-08-25-003):
  1. Journal entry is written BEFORE the .i64 is touched (write-ahead).
  2. Every patch records old + new bytes, so any entry can revert exactly.
  3. The journal lives next to the .i64 (``<stem>.patchlog.jsonl``) — the
     patched bytes live in the IDA database, never in the source binary.
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path


def journal_path(i64_path: str | Path) -> Path:
    p = Path(i64_path)
    return p.with_suffix(".patchlog.jsonl")


def append_entry(
    i64_path: str | Path,
    *,
    addr: int,
    old_bytes: bytes,
    new_bytes: bytes,
    mode: str,
) -> dict:
    """Write-ahead: append a journal entry and return it (with its id)."""
    entry = {
        "id": uuid.uuid4().hex[:12],
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "addr": addr,
        "addr_hex": hex(addr),
        "old_bytes": old_bytes.hex(),
        "new_bytes": new_bytes.hex(),
        "mode": mode,
        "reverted": False,
    }
    path = journal_path(i64_path)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def list_entries(i64_path: str | Path) -> list[dict]:
    path = journal_path(i64_path)
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # a torn last line must not hide the valid history
    return out


def find_entry(i64_path: str | Path, patch_id: str) -> dict | None:
    for e in list_entries(i64_path):
        if e["id"] == patch_id:
            return e
    return None


def mark_reverted(i64_path: str | Path, patch_id: str) -> None:
    """Rewrite the journal with the entry flagged (append-only semantics for
    history, but revert state must be queryable — so we rewrite the file)."""
    path = journal_path(i64_path)
    entries = list_entries(i64_path)
    for e in entries:
        if e["id"] == patch_id:
            e["reverted"] = True
            e["reverted_ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    path.write_text("".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8")


def decode_check(data: bytes, mode: str, addr: int = 0) -> dict:
    """Capstone-decode the patched window so the caller sees what the bytes
    MEAN. ``mode`` is "32" or "64" (from the binary's own bitness — the
    fork's machine-hint fix makes this reliable for 32-bit PEs).

    decode_ok=False is a WARNING, not a failure: data patches and
    intentional traps legitimately don't decode.
    """
    import capstone

    cs = capstone.Cs(capstone.CS_ARCH_X86,
                     capstone.CS_MODE_32 if mode == "32" else capstone.CS_MODE_64)
    insns = [f"{i.mnemonic} {i.op_str}".strip() for i in cs.disasm(data, addr)]
    return {"decode_ok": bool(insns), "decoded": insns[:16], "mode": mode}
