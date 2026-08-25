# Backend Portability Report — can a free backend serve spectrIDA?

**Date:** 2026-08-25 · **Author:** agent (tp-2026-08-25-003 Part B spike)
**Timebox:** one day · **Status:** final
**Question:** can the idalib-dependent backend be abstracted so a free
backend (r2pipe / Ghidra headless) serves `api.py`'s facade?

---

## 1. The consumed surface (enumerated from live code, not guessed)

Three consumers touch the backend: `api.py` (facade), `mcp_server.py`
(36 tools), the TUI (via `Backend` in `core/backend.py`). The operations
they actually consume, grouped by portability:

| Operation | Consumers | r2pipe can serve? | Ghidra headless? |
|---|---|---|---|
| `list_functions` | all three | ✅ `aflj` — yes, fast | ✅ yes |
| `disasm` | all three | ✅ `pdfj`/`aoj` | ✅ yes |
| `xrefs_to` / `xrefs_from` | all three | ✅ `axtj`/`axfj` | ✅ yes |
| `info` (func bounds) | api, TUI | ✅ `afij` | ✅ yes |
| `rename` | all three | ✅ `afn` | ✅ yes |
| `get_bytes` / `patch_bytes` | patch tools | ✅ `pxj`/`wx` (on the *file*, not a db — see §3) | ⚠️ program listing, savable |
| `decompile` | api, TUI, explain | ⚠️ `pdg` (r2dec, uneven) / `r2ghidra` plugin (good, needs install) | ✅ **excellent — the real prize** |
| `demangle` | api | ✅ `iD` / `bin.demangle` | ✅ yes |
| `flirt` | verify, MCP | ❌ `z` signatures exist but far weaker | ⚠️ FID — exists, weaker than IDA's FLIRT |
| `rtti` | MCP | ❌ no | ⚠️ partial via RTTI analyzers |
| `refs` / `knowledge` (IDB comments) | MCP | ❌ no equivalent | ⚠️ plate comments — partial |
| `bits` (db bitness) | patch verify | ✅ `iI`/`asm.bits` | ✅ yes |
| `.i64` round-trip (save/load db) | everything | ❌ **r2 projects are not analysis databases** | ✅ `.gpr` projects |

## 2. What the consumers actually need — the protocol sketch

The facade leaks no idalib types outward (dicts/lists of primitives
already — good). A `Backend` protocol is feasible:

```python
class AnalysisBackend(Protocol):
    capabilities: BackendCaps  # see below

    async def open(self, path: str) -> None: ...
    async def close(self) -> None: ...
    async def list_functions(self) -> list[dict]: ...
    async def disasm(self, addr: int) -> list[dict]: ...
    async def xrefs_to(self, addr: int) -> list[dict]: ...
    async def xrefs_from(self, addr: int) -> list[dict]: ...
    async def info(self, addr: int) -> dict | None: ...
    async def rename(self, addr: int, name: str) -> bool: ...
    async def get_bytes(self, addr: int, size: int) -> bytes | None: ...
    async def patch_bytes(self, addr: int, data: bytes) -> bool: ...
    async def bits(self) -> str: ...
    # capability-gated:
    async def decompile(self, addr: int) -> str: ...       # can_decompile
    async def demangle(self, names: list[str]) -> dict: ... # can_demangle
    async def flirt(self) -> dict: ...                      # can_flirt
    async def rtti(self) -> dict: ...                       # can_rtti
```

`BackendCaps` flags let the TUI/MCP degrade: no `can_decompile` → `D` key
shows "decompiler unavailable on this backend"; no `can_flirt` →
`apply_flirt` tool returns an explanatory error instead of garbage.

## 3. The three hard problems (this is where the cost lives)

1. **The database abstraction.** spectrIDA's whole model is *open a rich
   analysis database once, query forever*. idalib gives `.i64`; Ghidra
   gives `.gpr`. **r2pipe gives nothing comparable** — r2 re-analyzes on
   every open (minutes for large binaries) unless you hand-roll caching
   via projects. A r2 backend would be Ghidra-via-r2 (`r2ghidra`) for
   decompile anyway, so pure-r2 is the weak option.

2. **Analysis quality parity is not a UI problem.** IDA's function
   boundaries, FLIRT coverage, and type propagation are what make
   spectrIDA's shard counts and naming inputs trustworthy. Ghidra's
   analysis is genuinely good (often comparable, occasionally better on
   stack strings, usually weaker on FLIRT). r2's is noticeably weaker on
   anything non-trivial. The interface is a fortnight; *trusting the
   output* is the real work.

3. **The sharded pipeline is idalib-native.** `parallel_analyze.py` spawns
   N idalib subprocesses on zeroed shard binaries — that design assumes
   per-process database isolation. Ghidra headless can do this (analyze
   per shard via `-postScript`), but the shard-merge phase
   (`MERGE_LOADER`) is IDA IDAPython — a Ghidra port means rewriting the
   merge, the riskiest component.

## 4. Options

| Option | Cost | Value |
|---|---|---|
| **A. Stay IDA-only** | 0 | Focus effort on agent loop (tp-004) |
| **B. Protocol + Ghidra backend** | ~3–6 wks (incl. merge rewrite + quality validation) | Free users get the full pipeline; real prize is Ghidra's decompiler feeding explain/naming |
| **C. Protocol + r2pipe backend** | ~2–3 wks | Cheaper, but weaker analysis + no real db + still needs r2ghidra for decompile — worst value/cost ratio |
| **D. Protocol only, ship no second backend** | ~1 wk | Cleans the seam, defers the decision; no user-visible change |

## 5. Recommendation: **D now, B later, C never**

- **D (protocol extraction) now** — the facade is already type-clean;
  pinning a `Backend` protocol + `BackendCaps` costs little and makes the
  seam explicit. Do it as part of tp-004's agent work, which will touch
  the same layer.
- **B (Ghidra) later** — justified *only* if free-tier users actually
  appear. The decompiler is the one capability worth the port; the merge
  rewrite is the risk. Revisit after tp-004 lands.
- **C (r2pipe) never as a primary backend** — it cannot own the database
  role. r2 remains a fine *auxiliary* CLI for quick patching/triage
  outside the pipeline.

**Go/no-go on a free backend today: NO-GO** — not because it's infeasible,
but because the honest cost is the merge rewrite + quality validation,
and tp-004 (agent loop) delivers more value per week right now.

## 6. Evidence base

- Surface enumeration: `grep` over `api.py`, `mcp_server.py`,
  `core/ida.py`, `core/backend.py` at `af34c66` (tables in §1–2 are the
  actual consumed operations, not a guess at "what IDA does").
- r2/Ghidra capability claims are standard tool knowledge, flagged here as
  the one part **not** live-verified in this spike (no r2/Ghidra in the
  sandbox). If option B is ever green-lit, step one is a hands-on
  validation of the §1 table against a real Ghidra install.
