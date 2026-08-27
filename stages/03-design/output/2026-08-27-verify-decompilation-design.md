# Design — tp-2026-08-27-005: real `verify_decompilation` (differential oracle wiring)

**Status:** approved by owner directive ("your call: B, then A — build the verifier while the
patching muscle memory is fresh, then UAT both together", 2026-08-27)
**Stage:** 03-design → 04-build
**Decision chain:** dec-2026-08-25-002 #5 defined the stub contract; this packet replaces the stub.

## Goal

Replace the `verify_decompilation` MCP stub with the real pipeline:

```
function address → info() (size) → read_bytes (.i64) → bits() (32/64)
→ oracle.verify_function(original_bytes, pseudocode)
→ {verified: bool, status, reason, details}
```

The agent loop's planner already upgrades `VERIFY_THEN_QUEUE → AUTO_APPLY` on
`verified: true` (test-pinned in tests/test_agent.py) — **no planner or loop change**.

## Existing assets (discovered during recon — do not rebuild)

| Asset | Location | State |
|---|---|---|
| `verify_function` full pipeline (compile → extract → emulate ×2 → compare) | `spectrida/verify/oracle.py` | exists, x64-only, hardcoded gcc path |
| `get_bytes` worker command + `_ida.get_bytes` | `spectrida/core/ida.py` | exists, **not exposed** through RealBackend/IDADatabase |
| `bits` worker command + `_ida.bits` ("32"/"64") | `spectrida/core/ida.py` | exists, not exposed |
| Stub response contract (`verified` / `status`) | `spectrida/agent/planner.py:73` | test-pinned, unchanged |

## Build items

1. **Backend/API exposure** — `Backend.read_bytes(addr, size)`, `Backend.bits()`;
   RealBackend → `_ida.get_bytes` / `_ida.bits`; DemoBackend → canned bytes + "64";
   `IDADatabase.read_bytes()` / `IDADatabase.bits()` (bits cached per handle).
2. **oracle.py 32-bit support** — `emulate_function(..., bits=64)`: `UC_MODE_32`,
   cdecl stack args (`[esp+4]` onward), EAX return; `verify_function(..., bits=64)`
   threads it through and passes `-m32` to gcc when 32.
3. **Toolchain resolution cleanup** — `_find_tool("gcc")`: env `SPECTRIDA_GCC` →
   known WinLibs path → `shutil.which("gcc")/("g++")`. Same pattern for objdump.
   Missing toolchain is **data, not a crash** (see degradation contract).
4. **First-function extraction** — `extract_function_bytes(dll, "")` falls back to the
   first label in objdump output; `verify_decompilation` cannot know the function name
   inside caller-supplied C (contract: pseudocode must contain exactly one function).
5. **Wire the MCP tool** — single-shot verify (see deviation D2).

## Response contract (planner-compatible)

```jsonc
{
  "address": "0x...",
  "verified": true | false,          // planner upgrades ONLY on true
  "status": "verified" | "mismatch" | "inconclusive",
  "reason": "...",                    // oracle reason or degrade cause
  "details": "...",                   // return/memory comparison
  "pseudocode": "<first 500 chars>"
}
```

Degradation (all → `verified: false`, planner routes to HUMAN_QUEUE):
no function at address · bytes unreadable · function > 0x10000 bytes (emulator map
limit) · gcc/objdump absent (`no_toolchain`) · C fails to compile (raw Hex-Rays
output is **not** compilable C — expected; the intended input is model-rewritten C)
· emulation fault.

## Deviations from any earlier assumption (recorded, owner-visible)

- **D1 — 32-bit is in scope.** The live UAT target (target.exe) is x86-32; the oracle
  was x64-only. Bits are read from the live database, never assumed.
- **D2 — single-shot, no retry loop.** The stub's `max_attempts` implied
  compile→diff→rewrite retries; a real retry needs an LLM refinement pass per attempt.
  tp-005 ships single-shot; the parameter stays for forward compatibility and a future
  packet can add the refinement loop. Honest > half-built.
- **D3 — no planner/loop changes.** Contract was designed for this day; keep it pinned.
- **D4 — toolchain is a host dependency.** gcc + objdump must exist on the analysis
  machine. Absence degrades cleanly (HUMAN_QUEUE), matching dec-2026-08-25-002 #5's
  spirit: never fake a verdict.

## Acceptance criteria

1. Unit tests green: 64-bit + 32-bit emulation (hand-assembled bytes, incl. cdecl
   stack-arg read), compare tolerance, first-function extraction, MCP tool with faked
   db (verified / no-bytes / no-toolchain paths).
2. End-to-end gcc test (skipif no gcc): equivalent C → `verified: true`;
   mutated C → `verified: false`.
3. Full suite stays green; no regressions to agent/patch/explain tests.
4. Workspace records updated (episode + log + PROJECT_STATUS); WIP bundle refreshed.
5. Push only on explicit per-occasion owner authorization (device flow).
