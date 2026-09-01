# Episode — 2026-09-01 — verify_decompilation live UAT (Phases 0–3, BlackTie)

**Status:** draft (agent-authored, pending human approval)
**Scope:** first live run of the real verifier (tp-005) against target_parallel.i64
on the BlackTie machine (IDA Pro 9.0, spectrida-re, Neo4j Desktop, 12 GB VRAM).

## Outcome

PASS. GOOD candidate C → `verified: true`; mutated C → `mismatch` on return value.
Full chain exercised live: graph registry → idalib open → `info`/`read_bytes`/`bits`
→ MinGW compile → objdump extract → Unicorn emulate (32-bit, database-reported
bitness) → tolerance compare.

## Four bugs found live, all fixed and regression-pinned

1. **mcp 2.x broke every tool import** — `pip install -e ".[graph]"` resolved
   `mcp>=1.0` to 2.1.1, which removes `mcp.server.fastmcp`. Pinned `mcp>=1.0,<2`
   (1589a36) + test. *Lesson: upstream majors rename APIs; caps are cheap.*
2. **objdump env override never wired** — `_find_tool("objdump")` existed but
   `extract_function_bytes` shelled out to bare `objdump` on PATH (8836f69).
   *Lesson: adding a resolver isn't enough; grep every call site.*
3. **unicorn missing from [graph] extra** — verifier is reachable via MCP, not
   only [atlas]; fresh install died at the emulation leg (5ebeee4).
4. **Stack-frame writes false-mismatched equivalent functions** — the deepest
   one: MSVC original wrote 3 stack slots, MinGW -O2 recompile wrote 1, returns
   matched, memory compare said MISMATCH. Stack traffic is compiler artifact,
   not behavior; oracle now compares return value + non-stack writes only
   (63513f1). *Lesson: define "behavior" before you compare it.*

## Operator-side lessons (for the quickstart)

- PowerShell expands `$var` inside double quotes — the Neo4j password
  (`1802698$Mar`) silently became `1802698` until backtick-escaped.
- Copy-pasted placeholder paths (`C:\...\mingw64\bin\gcc.exe`) fail politely
  through the degrade contract — but `Test-Path` first saves a round trip.
- winget PATH changes need a new shell; `SPECTRIDA_GCC`/`SPECTRIDA_OBJDUMP`
  env overrides sidestep that entirely.

## Known cosmetics (not bugs)

- Neo4j `IF NOT EXISTS` schema notifications spam INFO logs on every startup.
- Windows asyncio prints "Event loop is closed" at interpreter exit after
  idalib subprocess use — cosmetic, exit-time only.

## Next

Phase 4: `agent_run` live with the real verifier in the loop (bounded budgets:
20 LLM / 5 renames / 10 min). Then the recorded TODOs: idalib worker stderr
capture, silent open_database exit.
