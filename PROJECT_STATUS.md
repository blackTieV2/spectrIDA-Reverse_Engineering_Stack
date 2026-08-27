---
type: project-status
project: "spectrida-re-stack"
status: active
current_stage: 05-qa (awaiting user-side live acceptance)
execution_hold: true
build_approved: true
qa_approved: false
target_repo: "https://github.com/blackTieV2/spectrIDA-Reverse_Engineering_Stack"
approved_branch: "master"
approved_base: "c1c0570"
target_head: "origin/master = 68de72e (all builds pushed 2026-08-25)"
working_tree_owner: ""
last_reviewed: "2026-08-25"
---

# PROJECT_STATUS — spectrIDA (blackTieV2 fork)

## What this project is

A personal fork of `ggfuchsi-oss/spectrIDA-Reverse_Engineering_Stack`:
parallel IDA Pro (idalib) binary analysis + local AI function naming
(Qwen3-8B via Ollama) + Neo4j knowledge graph + MCP server + phantomrt
dynamic layer (Unicorn/Frida/fuzzing).

## Current focus

Hardening complete. Feature program (4 task packets from the RE-tools
sidebar evaluation) complete: all designed, built, tested (94/94), and
pushed. Next: user-side live acceptance, then the Professor-track
learning exercise on a simple x86 Windows PE.

## Completed (user-authorised, 2026-08-25)

**Hardening series:**
- fix(build): lz4/capstone/numpy declared as base dependencies
- fix(analysis): torch import guarded — CPU-only installs no longer
  silently return zero functions
- fix(analysis): 32-bit x86 PEs decode via CS_MODE_32
- fix(analysis): Windows-hardcoded IDA/output paths replaced with
  platform-aware defaults
- chore: committed `desktop/node_modules` removed; dev codegen scripts
  relocated to `scripts/dev/`; gitignore `output/` rule anchored

**Feature program (task packets, stages/03-design/output/):**
- tp-001 Explain mode: versioned prompt contract + tolerant parser;
  TUI `E` key with streaming; MCP `explain_function`
- tp-002a Dynamic feedback: dyn_* provenance (source, run_id), draft OKF
  crash cards, TUI marker column ✖/▶/?  (scope revised after live-state
  falsification — see ep-2026-08-25-004)
- tp-003 Verified patching: journal-before-write, read-back verify with
  auto-revert, Capstone decode in binary bitness; backend-portability
  report → NO-GO for free backend today (dec-2026-08-25-002 #3)
- tp-004 Agent loop: `spectrida/agent/` (budget/planner/memory/report/
  loop), MCP `agent_run`/`agent_status`; bounded, draft-only, in-process

**Tests:** 94/94 passing (35 at session start).

## Known issues (open)

- `spectrida/verify/` + `spectrida/memory/`: 229 pre-existing ruff errors;
  upstream CI lint step was already red. Not remediated (out of scope).
- `verify_decompilation` MCP tool is a stub (returns
  `ready_for_verification`). Agent loop degrades medium-confidence names
  to the human queue until the real verifier lands (dec-2026-08-25-002 #5).
- ruff not run on 002a/003/004 code (sandbox PyPI down); py_compile +
  AST scan used instead. Run `ruff check spectrida/` on operator machine.
- Benchmark numbers in README are self-reported upstream; unverifiable
  without IDA Pro 9.x licence + the same hardware.
- `diaphora_*` MCP tools require a Diaphora checkout two levels above the
  package; undocumented upstream.
- **TODO (bug, fix next build):** `core/ida.py open_ida()` spawns the
  idalib worker with `stderr=asyncio.subprocess.DEVNULL` — when the worker
  dies before its @@RESP handshake, the user gets only "idalib worker
  exited unexpectedly" with zero evidence (hit live 2026-08-26 during the
  patch round-trip gate). Fix: capture stderr, include the tail in the
  RuntimeError; the regression test must name the real error text
  observed on the operator machine.
- **TODO (investigate):** `idapro.open_database(.i64)` exits the process
  silently (no rc, no traceback) when the database is already open in
  another idalib process (single-opener rule) — confirm and, if true,
  fail fast with a clear "database is open elsewhere" message.
- phantomrt is alpha (0.1.x); treat verdicts as leads, not proof.

## Execution hold

**ACTIVE.** Consequential action (merge upstream, push to shared remotes,
release, dependency upgrades) requires explicit user approval, per
occasion. All pushes to date were individually authorised.

## Next safe action

User-side live acceptance (operator machine only):
1. `spectrida formats` + `onboard` — IDA discovery (Lesson 1 checkpoint)
2. Compile target.c (`cl /Od /Zi /MT`) → verify machine type 0x14c
3. `spectrida --demo` — E key + marker column
4. ~~Patch/revert round-trip~~ ✅ DONE 2026-08-27 (journal-before-write,
   verified apply, Capstone decode `ret`, exact revert — after fixing the
   patch_bytes void-return bug live, 81f643a)
5. `ruff check spectrida/`
6. `agent_run` once Neo4j is live → review draft report

Then: protocol extraction (option D) as a follow-up packet **if** the
agent loop's observed live call pattern justifies it (per Part B
recommendation — deliberately deferred, not forgotten).
