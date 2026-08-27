# Episode — 2026-08-27 — verify_decompilation becomes real (tp-2026-08-27-005)

**Status:** draft (agent-authored, pending human approval)
**Owner directive:** "your call: B, then A — build the verifier while the patching
muscle memory is fresh, then UAT both together."

## What happened

The `verify_decompilation` MCP tool was a stub returning
`status: ready_for_verification` (dec-2026-08-25-002 #5 — degrade medium-confidence
renames to the human queue while the verifier was unbuilt). Recon revealed the whole
pipeline already existed in pieces:

- `spectrida/verify/oracle.py` had the full differential oracle (compile C → extract
  bytes → Unicorn emulate both → tolerance compare) — x64-only, with one machine's
  WinLibs path hardcoded.
- The idalib worker already answered `get_bytes` and `bits` (tp-003) — but nothing
  above the `_ida` module layer could reach them.

So tp-005 was **wiring, not inventing**: expose `read_bytes`/`bits` through
Backend → IDADatabase, teach the oracle 32-bit (the live UAT target is x86-32),
resolve gcc/objdump like a tool not a souvenir, and connect the MCP tool.

## Decisions (full packet: stages/03-design/output/2026-08-27-verify-decompilation-design.md)

- **D1 — 32-bit in scope.** Bitness is read from the live database (`bits()`),
  never assumed. UC_MODE_32 + cdecl stack args + EAX.
- **D2 — single-shot.** The stub's `max_attempts` implied a retry loop; a real retry
  needs an LLM refinement pass per attempt. Parameter kept, loop deferred. Honest >
  half-built.
- **D3 — planner untouched.** The `verified:true → AUTO_APPLY` upgrade path was
  test-pinned in tp-004 exactly for this day. It just works.
- **D4 — toolchain absence is data.** No gcc/objdump → `status: no_toolchain`,
  `verified: false` → human queue. Raw Hex-Rays pseudocode isn't compilable C and
  degrades the same way; the intended input is model-rewritten C containing exactly
  one function.

## Evidence

- tests/test_verify.py: 18 tests (hand-assembled 32/64-bit byte pairs incl. cdecl
  stack-arg reads, tolerance oracle, first-function extraction, MCP tool with faked
  live db, gcc end-to-end skipif'd). Suite: 106 → 124 green.
- Commits: 3c2cc04 (oracle) · cc852ad (api) · b3c02b7 (mcp wiring) · dc86eaf (tests+packet).

## Sandbox gotcha worth remembering

mcp 1.12.4 (pin from a stale resolution) chokes on PEP 563 string annotations at
tool-registration time (`issubclass(param.annotation, Context)`). The user's live
environment runs a newer 1.x and is unaffected. If the sandbox MCP import ever
fails that way: `pip install -U "mcp<2"`, don't "fix" the source.

## What's next

Live UAT of `agent_run` with the real verifier on the BlackTie machine — needs
gcc + objdump on PATH there (WinLibs or MSYS2) or medium-confidence items will
degrade to the queue by design. Then the two recorded fixes: idalib worker stderr
capture, silent open_database exit.
