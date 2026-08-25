---
id: "tp-2026-08-25-003"
type: task-packet
title: "Binary patching (verified write-back with undo) + backend-portability spike"
status: awaiting-build-approval
project: "spectrida-re-stack"
stage: "03-design"
created_at: "2026-08-25"
head_at_design: "f8ab962"
depends_on: []
---

# Task

Two separable deliverables, one packet because they share a theme
(spectrIDA stops being read-only / single-backend):

**A. Binary patching** — an `apply_patch` capability with a hard safety
contract: write bytes → read-back verify → Capstone re-decode check →
journal entry for undo. Surfaces: MCP tool + Python API + (stretch) TUI.

**B. Backend-portability spike** — a *timeboxed investigation*, not an
implementation: can the idalib-dependent `RealBackend` be abstracted so a
free backend (r2pipe or Ghidra headless) can serve `api.py`'s facade?
Output is a go/no-go report with a cost estimate, not code.

Splitting A from B matters: A is days, B is the largest single decision in
the project's future. They ship independently.

# Stage

03-design. This document is the only output. Build requires explicit user
approval.

# Current Verified State

Verified by live re-read at `f8ab962`:

- The codebase is **read-only on bytes today**: write operations that
  exist are metadata-only — `idc.set_name` (core/ida.py lines 64, 253) and
  `idc.set_cmt` (line 255). No `ida_bytes.patch_*` call exists anywhere
  (grep-verified).
- `spectrida/core/ida.py` is the idalib RPC layer where a patch op belongs.
- `spectrida/api.py` facade: thin async wrapper — `rename` (line 118) is
  the mutation pattern to mirror.
- Format handler contract (`analysis/formats/base.py`): `read_bytes`
  (line 105) gives byte-level access to prepared images — the read-back
  half of verification already exists at the format layer.
- Plugin discovery (`analysis/formats/registry.py`): handlers found via
  module-level `HANDLER` + `spectrida.formats` entry-point group. **This
  registry is format-level** (ELF/PE/NSO detection + sharding), NOT an
  analysis-backend abstraction — the idalib backend is currently
  hard-wired into `core/ida.py` and `api.py`. Any "Ghidra backend" requires
  a new abstraction layer. This is the honest core finding for part B.
- Capstone is a base dependency (we made it one) — decode verification of
  patched bytes costs nothing extra.

# Read

1. `AGENTS.md` → `PROJECT_STATUS.md` → this packet
2. `spectrida/core/ida.py` lines 40–80 and 240–260 (existing write ops)
3. `spectrida/analysis/formats/base.py` (the full contract — 160 lines)
4. `spectrida/analysis/formats/registry.py`
5. `spectrida/api.py` `rename` + `IDADatabase` facade

# Relevant Prior Experience

> Historical hints only. Current verified target state controls execution.

- `ep-2026-08-25-001`: the 0x06 decode-mode distinguisher (valid in
  32-bit, invalid in 64-bit) proved Capstone mode selection is subtle and
  testable. → Patch verification reuses that test's mode-aware decoder.
- `dec-2026-08-25-001`: additive-only. → Patching adds a new op; the
  read-only pipeline is untouched; patching is never invoked implicitly
  (no auto-patch "helpful" fixups, ever).
- Workspace doctrine: irreversible-ish actions need evidence. → Every
  patch produces a journal entry *before* the write, not after.

# Design

## Part A — Binary patching

### A.1 Core op (`core/ida.py`)

```python
patch_bytes(addr, data: bytes, *, expect_mode: str | None = None) -> PatchResult
```

Sequence (all-or-nothing contract):

1. **Pre-journal**: append `{ts, addr, old_bytes, new_bytes}` to
   `<i64_dir>/patches/<name>.patchlog.jsonl` *before* touching the db.
2. `ida_bytes.patch_bytes` via idalib.
3. **Read-back**: `read_bytes` at `addr` must equal `data` — else
   auto-revert from the journal and raise.
4. **Decode check**: Capstone re-disassemble the patched window in the
   binary's mode (32/64 from the PE machine hint — the fork's fix makes
   this reliable); result includes the decoded instruction list so the
   caller sees what the bytes *mean*. A patch that doesn't decode cleanly
   is reported with `decode_ok: false` (warning, not auto-revert — NOP
   sleds and intentional traps decode fine, data patches legitimately
   don't).

### A.2 Surfaces

- MCP tool `apply_patch(binary, address, hex_bytes, verify: bool = True)`
  → dict with old/new bytes, read-back status, decoded instructions.
- `api.py`: `IDADatabase.patch(address, data)` mirroring `rename`.
- MCP tool `list_patches(binary)` + `revert_patch(binary, patch_id)` —
  the journal makes undo a first-class citizen.
- TUI: **deferred to a follow-up packet** (patch UI deserves its own
  design: diff preview, confirm dialog). A keystroke that writes bytes
  should not be designed in a sidebar of this packet.

### A.3 Scope discipline

Patching writes to the **`.i64`**, not the original binary on disk.
Exporting a patched binary is a separate feature (IDA's own
"Apply patches to input file" flow) — explicitly out of scope.

## Part B — Backend-portability spike (timeboxed)

**Investigation only**, max one working day of agent effort. Questions:

1. What is the exact surface `api.py`/`mcp_server.py`/TUI actually consume
   from idalib? (Enumerate: list_functions, disasm, decompile, xrefs,
   rename, comments, FLIRT, RTTI…)
2. Which of those can r2pipe serve acceptably (disasm ✓, xrefs ✓, decompile
   via r2dec/r2ghidra ~okay, FLIRT ✗, RTTI ✗)?
3. What does a `Backend` protocol look like, and what capability flags
   (`can_decompile`, `can_flirt`, …) must it expose so the TUI degrades
   gracefully on a free backend?

**Deliverable:** `stages/02-research/output/backend-portability-report.md`
with a capability matrix, a proposed `Backend` protocol, and a go/no-go
recommendation with honest cost (expectation: protocol extraction is
weeks; the hard part is not the interface, it's matching idalib's
analysis quality).

# Files touched (complete list, Part A only — Part B writes one report)

| File | Change |
|---|---|
| `spectrida/core/ida.py` | `patch_bytes` + read-back + journal |
| `spectrida/core/patchlog.py` | **new** — JSONL journal, revert logic |
| `spectrida/api.py` | facade `patch`, `list_patches`, `revert_patch` |
| `spectrida/mcp_server.py` | `apply_patch`, `list_patches`, `revert_patch` tools |
| `tests/test_patch.py` | **new** — journal, read-back, decode check, revert |
| `stages/02-research/output/backend-portability-report.md` | **new** (Part B) |

# Approved Scope

The six entries above. Commits (expected): `feat(core): patch journal +
verified patch_bytes` → `feat(mcp): apply_patch/list_patches/revert_patch`
→ `test: patch safety contract` → `docs(research): backend portability
report`.

# Permitted Tools

pytest, ruff (changed files), git local commits, existing deps (idalib is
mocked in tests; Capstone already a base dep).

# Prohibited Actions

- Pushing without per-occasion authorisation.
- Any auto-patching (no heuristic "fix-ups" applied without an explicit
  user/agent call per patch).
- Writing to the original input binary on disk.
- Building the actual Ghidra/r2 backend — Part B is a report, not code.
- New dependencies; TUI patch UI (follow-up packet).

# Stop Conditions

Stop if: idalib's `ida_bytes` API in the installed IDA version lacks the
needed calls (version drift — report, don't shim); the journal can't be
made atomic enough (journal-before-write is the safety floor); Part B
enumeration shows the facade leaks idalib types so deeply that a protocol
extraction would rewrite the TUI (then no-go, recommend staying IDA-only).

# Acceptance Criteria

**Automated (sandbox):**

1. Journal written before write; revert restores exact old bytes;
   read-back mismatch triggers auto-revert + raise.
2. Decode check uses CS_MODE_32 for 32-bit images (the fork's arch-hint
   path), CS_MODE_64 otherwise — pinned by tests reusing the 0x06
   distinguisher trick.
3. Full suite green; ruff clean on changed files.

**Live (user's machine):**

4. Patch two bytes of `target.exe`'s `add` (e.g. `01 d8` → `29 d8`,
   add→sub) in the `.i64`; re-decompile shows the change; `revert_patch`
   restores; the original `target.exe` on disk is byte-identical before
   and after.

**Part B:**

5. Report delivered with capability matrix + protocol sketch + go/no-go.

# Required Evidence

- pytest output; the patch journal file; before/after decompilation of
  the patched function; sha256 of `target.exe` pre/post (criterion 4);
  run record; episode record post-build.

# Final Report

To be appended by the build agent: commits, evidence, deviations,
Part B recommendation summary.

# Rollback

Part A: revert commits; journals are inert data. Part B: a report file —
delete it.

# Risks

| Risk | Mitigation |
|---|---|
| Patch corrupts the analyst's only `.i64` | Journal-before-write + auto-revert on read-back mismatch + patches live in `.i64`, never the source binary |
| User mistakes `.i64` patching for binary patching | Tool docstrings and MCP descriptions state it explicitly |
| Part B report becomes an unbounded research hole | Hard timebox + three fixed questions; no implementation permitted |
| Scope creep merges A and B | They ship as separate commit series; B cannot block A |
