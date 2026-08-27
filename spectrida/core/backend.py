"""The data backend the TUI talks to — real (idalib + Ollama) or demo (canned).

Screens never branch on demo-vs-real; they hold a Backend and call its async
methods. `stream_name` takes everything either backend might need; each uses
what's relevant.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

from spectrida.core import demo as _demo
from spectrida.core import explain as _explain
from spectrida.core import ida as _ida
from spectrida.core import ollama as _ollama


class Backend:
    title: str = ""
    demo: bool = False

    async def ensure_open(self) -> None:
        return None

    async def list_functions(self) -> list[dict]: ...
    async def disasm(self, addr) -> list[dict]: ...
    async def decompile(self, addr) -> str: ...
    async def xrefs_to(self, addr) -> list[dict]: ...
    async def xrefs_from(self, addr) -> list[dict]: ...
    async def rename(self, addr, name: str) -> bool: ...
    async def demangle(self, names: list[str]) -> dict[str, str]: ...
    async def info(self, addr) -> dict | None: ...
    async def flirt(self) -> dict: ...
    async def rtti(self) -> dict: ...
    async def refs(self, addr) -> dict: ...
    async def knowledge(self, addrs: list[str]) -> list[dict]: ...
    async def write_name(self, addr, name: str, comment: str = "") -> bool: ...
    def stream_name(self, addr, insns, callees, callers) -> AsyncIterator[str]: ...
    def stream_explain(self, addr, insns, context_block: str, pseudocode: str) -> AsyncIterator[str]: ...
    async def dyn_flags(self, addrs: list[int]) -> dict[int, str]:
        return {}
    async def verified_patch(self, addr, data: bytes) -> dict: ...
    async def list_patches(self) -> list[dict]: ...
    async def revert_patch(self, patch_id: str) -> dict: ...
    async def read_bytes(self, addr, size: int) -> bytes | None: ...
    async def bits(self) -> str: ...
    async def close(self) -> None: ...


class RealBackend(Backend):
    def __init__(self, i64: str) -> None:
        self.i64 = i64
        self.title = Path(i64).stem.replace("_parallel", "")
        self._ida: _ida.IDAHandle | None = None
        self._opened = False

    async def open(self) -> None:
        self._ida = await _ida.open_ida(self.i64)
        self._opened = True

    async def ensure_open(self) -> None:
        if not self._opened:
            await self.open()

    async def list_functions(self):  return await _ida.list_functions(self._ida)
    async def disasm(self, addr):    return await _ida.disasm(self._ida, addr)
    async def decompile(self, addr): return await _ida.decompile(self._ida, addr)
    async def xrefs_to(self, addr):  return await _ida.xrefs_to(self._ida, addr)
    async def xrefs_from(self, addr): return await _ida.xrefs_from(self._ida, addr)
    async def rename(self, addr, name): return await _ida.rename(self._ida, addr, name)
    async def demangle(self, names): return await _ida.demangle(self._ida, names)
    async def flirt(self):     return await _ida.flirt(self._ida)
    async def rtti(self):      return await _ida.rtti(self._ida)
    async def refs(self, addr):    return await _ida.refs(self._ida, addr)
    async def knowledge(self, addrs): return await _ida.knowledge(self._ida, addrs)
    async def write_name(self, addr, name, cmt=""): return await _ida.write_name(self._ida, addr, name, cmt)


    async def info(self, addr): return await _ida.info(self._ida, addr)

    def stream_name(self, addr, insns, callees, callers):
        return _ollama.stream_name(insns, callees, callers)

    def stream_explain(self, addr, insns, context_block, pseudocode):
        return _explain.stream_explain(
            insns, context_block=context_block, pseudocode=pseudocode)

    async def dyn_flags(self, addrs):
        """Runtime-evidence markers from the graph (if one is configured).

        ▶ executed (live trace or clean fuzz) · ✖ candidate crash ·
        ? needs_state. Any failure -> {} (markers are decoration, never
        a reason to break the TUI)."""
        try:
            from spectrida.core.graph import FunctionGraph
            from spectrida import config
            g = FunctionGraph(config.graph_uri(), config.graph_user(),
                              config.graph_password())
        except Exception:
            return {}
        try:
            import asyncio
            def _query():
                marks: dict[int, str] = {}
                with g.driver.session() as s:
                    rows = s.run(
                        "MATCH (f:Function) WHERE f.addr IN $addrs "
                        "RETURN f.addr AS addr, f.dyn_status AS st, "
                        "f.dyn_crashes AS crashes, f.dyn_live_ran AS ran",
                        addrs=list(addrs))
                    for r in rows:
                        st, crashes, ran = r["st"], r["crashes"], r["ran"]
                        if (crashes or 0) > 0 or st == "candidate_crash":
                            marks[r["addr"]] = "\u2716"
                        elif ran or st == "exercised_clean":
                            marks[r["addr"]] = "\u25b6"
                        elif st == "needs_state":
                            marks[r["addr"]] = "?"
                return marks
            return await asyncio.to_thread(_query)
        except Exception:
            return {}

    async def close(self):
        if self._ida:
            await self._ida.close()


    async def verified_patch(self, addr, data):
        return await _ida.verified_patch(self._ida, addr, data)

    async def list_patches(self):
        from spectrida.core import patchlog
        return patchlog.list_entries(self._ida.i64)

    async def revert_patch(self, patch_id):
        return await _ida.revert_patch(self._ida, patch_id)

    async def read_bytes(self, addr, size: int):
        return await _ida.get_bytes(self._ida, addr, size)

    async def bits(self):
        return await _ida.bits(self._ida)


class DemoBackend(Backend):
    demo = True
    title = "demo.dll"

    def __init__(self) -> None:
        self._funcs = [dict(f) for f in _demo.FUNCTIONS]

    async def list_functions(self):  return self._funcs
    async def disasm(self, addr):    return _demo.disasm(addr)
    async def decompile(self, addr): return _demo.decompile(addr)
    async def xrefs_to(self, addr):  return _demo.xrefs_to(addr)
    async def xrefs_from(self, addr): return _demo.xrefs_from(addr)

    async def rename(self, addr, name):
        a = addr if isinstance(addr, int) else int(str(addr), 16)
        for f in self._funcs:
            if f["start"] == a:
                f["name"] = name
                return True
        return True

    async def read_bytes(self, addr, size: int):
        return b"\x55\x8b\xec" + bytes(max(0, size - 4)) + b"\xc3"  # canned prologue…ret

    async def bits(self):
        return "64"

    def stream_name(self, addr, insns, callees, callers):
        return _demo.stream_name(addr)

    def stream_explain(self, addr, insns, context_block, pseudocode):
        return _demo.stream_explain(addr)

    async def dyn_flags(self, addrs):
        # canned: one crashed, one traced, one needs_state — shows the column
        return {0x1400013A0: "\u2716", 0x140001100: "\u25b6",
                0x140001600: "?"} if any(a in addrs for a in
                (0x1400013A0, 0x140001100, 0x140001600)) else {}

    async def demangle(self, names):
        return {}

    async def info(self, addr):
        return None

    async def close(self):
        return None


async def make_backend(*, demo: bool = False, i64: str | None = None) -> Backend:
    if demo or not i64:
        return DemoBackend()
    b = RealBackend(i64)
    await b.open()
    return b
