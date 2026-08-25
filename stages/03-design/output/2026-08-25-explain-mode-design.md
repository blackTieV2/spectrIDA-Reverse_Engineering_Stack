---
id: "tp-2026-08-25-001"
type: task-packet
title: "Explain mode — MCP tool, TUI binding, prompt contract"
status: approved
project: "spectrida-re-stack"
stage: "03-design"
created_at: "2026-08-25"
head_at_design: "f8ab962"
---

# Task

Implement **Explain mode**: one-keystroke, natural-language explanation of the
selected function, delivered through three coordinated additions:

1. **Prompt contract** (`spectrida/core/explain.py`) — a versioned system/user
   prompt pair producing a *parseable* structured explanation.
2. **MCP tool** (`explain_function`) — exposes explanation to any MCP client,
   reusing the existing graph-context machinery.
3. **TUI binding** (`E` key) — streams the explanation live into the existing
   disasm pane, including in `--demo` mode (no IDA required).

Non-goal for v1: writing explanations into the `.i64` as comments (mutation;
candidate for a follow-up packet), the autonomous agent loop (separate
design), batch explain.

# Stage

03-design. Build approved by the user 2026-08-25 (execution_hold remains
active for consequential actions: pushing requires per-occasion approval).

# Current Verified State

Verified by live re-read of the clone at `f8ab962` on 2026-08-25:

- `spectrida/core/ollama.py` — `stream_name(insns, callees, callers)` streams
  from `{ollama_url()}/api/generate` with `system=_SYSTEM`, `temperature 0.2`,
  `num_predict 256`; `_build_prompt` caps disasm at 80 instructions, callers/
  callees at 8 names each; `extract_name` parses the `NAME:` line.
- `spectrida/context.py` — `gather_context(...)` (line 207) returns a
  `FunctionContext` with ranked callers/callees (named-first, hop distance),
  referenced string literals, distinctive constants;
  `format_context_block(ctx)` (line 266) renders it as a prompt block.
- `spectrida/mcp_server.py` — 32 tools; `get_context` is the reference
  pattern: `_norm_addr(address)`, `await _live_db(binary)` with graph
  fallback, dict return. `baseline_naming` exists but only *measures* naming
  coverage — it does not explain.
- `spectrida/api.py` — backend facade: `disasm`, `decompile`, `xrefs_to`,
  `xrefs_from`, `stream_name_tokens`, `overview`; `DemoBackend` exists and
  serves canned data (powers `--demo`).
- `spectrida/tui/screens/browser.py` — `BINDINGS` list (lines 25–34);
  `action_name_func`/`_stream_name` is the streaming-into-widgets pattern
  with `_busy` guard and spinner widgets; `action_chain_func` shows the
  DisasmPane-as-report-view pattern used by Explain's renderer.
- No current explain capability exists anywhere in the tree (grep-verified:
  no "explain" symbols outside this packet's design).
- Test suite at `f8ab962`: 35 passed. Ruff: 229 pre-existing errors in
  `spectrida/verify/` + `spectrida/memory/` (out of scope, do not touch).

# Read

Before building, read in this order:

1. `AGENTS.md` → `PROJECT_STATUS.md` → `stages/03-design/CONTEXT.md`
2. This packet
3. `spectrida/core/ollama.py` (whole file — it is 79 lines)
4. `spectrida/context.py` lines 200–290 (`gather_context`, `format_context_block`)
5. `spectrida/mcp_server.py` — the `get_context` tool body
6. `spectrida/tui/screens/browser.py` lines 100–280 (chain + naming actions)
7. `spectrida/api.py` — `IDADatabase` facade and `DemoBackend`

# Relevant Prior Experience

> Historical hints only. Current verified target state controls execution.

- `ep-2026-08-25-001` (upstream audit): READMEs are marketing; verify every
  claim against code on a clean environment. → This packet cites only
  re-verified facts.
- `ep-2026-08-25-002` (push + housekeeping): post-action review catches real
  gaps (missing handoff, unanchored gitignore). → Acceptance criteria below
  include a post-build workspace-record update, not just green tests.
- `dec-2026-08-25-001`: hardening scope stayed additive; behavior changes to
  existing paths were prohibited. → Same rule here: **naming output must be
  bit-identical after this feature lands** (snapshot-tested).

# Design

## 1. Prompt contract (`spectrida/core/explain.py`, new module)

System prompt (constant `EXPLAIN_SYSTEM`, v1):

```
You are an expert reverse engineer. Given disassembly and call-graph
context for ONE function, explain what it does for a working analyst.
Rules: be concrete; cite evidence (strings, constants, callees); admit
uncertainty instead of inventing behaviour; never claim to know the
original source name.
```

User prompt = `format_context_block(ctx)` (reuse) + disasm slice (80-insn
cap, existing `_insn_line` rendering) + optional pseudocode tail
(≤ 4000 chars, appended only when `include_pseudocode=True`).

**Output contract (parseable, versioned):**

```
PURPOSE: <one sentence>
BEHAVIOR:
1. <step>
2. <step>
INPUTS: <arguments / globals read, or "none evident">
OUTPUTS: <return value / globals written, or "none evident">
SIDE_EFFECTS: <I/O, memory allocation, calls with side effects, or "none">
SUGGESTED_NAME: <snake_case>
CONFIDENCE: high|medium|low — <one clause why>
```

Parser `parse_explanation(text) -> Explanation` (dataclass) is **tolerant**:
missing sections → empty fields, never raise; extra prose → preserved in
`raw`. `CONFIDENCE` value validated against {high, medium, low}, else
`unknown`. This tolerance is what makes the feature safe against model
drift — a malformed answer degrades to plain text display, not an exception.

Generation options: `temperature 0.2`, `num_predict 512` (explanations need
more headroom than names' 256; bounded so a rambling model can't stall the
TUI). Model/URL: existing `ollama_model()`, `ollama_url()` — **no new
config keys in v1**.

## 2. Shared streaming transport (minimal, guarded refactor)

Extract the httpx streaming loop from `stream_name` into a public
`stream_generate(system, prompt, num_predict) -> AsyncIterator[str]` in
`ollama.py`. `stream_name` is re-pointed at it with **identical payload
parameters**; `_SYSTEM`, `_build_prompt`, `extract_name` untouched. A
snapshot regression test pins `_build_prompt` output for fixed inputs so
the refactor cannot silently alter naming.

Rationale for extraction vs. duplication: the loop contains real error
handling (`chunk["error"]` → `RuntimeError`); two copies will drift.
Extraction is ~20 lines moved, zero behavior change, snapshot-tested.

## 3. Context assembly — two paths, one core

New pure function in `explain.py`:

```python
build_explain_prompt(*, insns, pseudocode, context_block) -> str
```

All inputs are plain data. Callers supply them:

- **MCP path** (`explain_function` in `mcp_server.py`): `_norm_addr` →
  `await _live_db(binary)` for disasm + pseudocode (graph fallback for
  pseudocode, exactly as `get_context` does) → `gather_context(_g(), ...)` +
  `format_context_block` → assemble → stream to completion → return dict:

  ```python
  {"address": hex, "explanation": Explanation-as-dict,
   "context": {"strings": n, "callers": n, "callees": n},
   "model": str, "elapsed_ms": int}
  ```

- **TUI path**: the live backend already provides `disasm`, `decompile`,
  `xrefs_to/from`; no graph exists in this process, so `context_block` is
  built from the xref lists + strings extracted from the disasm operand
  text (ASCII literals between quotes — cheap regex, no IDA dependency).
  Degraded-context explanations are still useful; the prompt contract's
  uncertainty rule covers the gap.

## 4. MCP tool `explain_function`

Signature:
`explain_function(binary: str, address: str, depth: int = 2, max_neighbors: int = 10, include_pseudocode: bool = True) -> dict`

Follows the `get_context` pattern verbatim (norm → live db → graph
fallback → dict). Raises `RuntimeError` with an actionable message when
Ollama is unreachable ("start Ollama or set [ollama] base_url") — MCP
clients surface this as a tool error, which is correct behaviour.

## 5. TUI binding (`spectrida/tui/screens/browser.py`)

- `Binding("e", "explain_func", "Explain")` appended to `BINDINGS`.
- `action_explain_func` mirrors `action_name_func`'s guards
  (`_cur is None` → notify; `_busy` → notify), then
  `_spawn(self._stream_explain())`.
- `_stream_explain` renders into `DisasmPane` (the `action_chain_func`
  report-view pattern): header `EXPLANATION ▸ <name>`, sections styled as
  they stream; `D` or re-selecting a function restores disasm. Reuses the
  existing model spinner widgets.
- `DemoBackend` gains a canned token stream so `spectrida --demo` shows the
  full feature with zero infrastructure — this is also how the feature is
  demoed/validated without IDA.

## 6. API surface (`spectrida/api.py`)

`IDADatabase` facade + `DemoBackend` each gain
`stream_explain(address, *, include_pseudocode=True) -> AsyncIterator[str]`.
Facade keeps its existing thinness: gather data → call `core.explain`.

## Files touched (complete list)

| File | Change |
|---|---|
| `spectrida/core/explain.py` | **new** — prompt contract, parser, prompt builder, streaming |
| `spectrida/core/ollama.py` | extract `stream_generate`; `stream_name` re-pointed (behavior-pinned) |
| `spectrida/mcp_server.py` | add `explain_function` tool (33rd tool) |
| `spectrida/api.py` | `stream_explain` on facade + DemoBackend |
| `spectrida/tui/screens/browser.py` | `E` binding, `_stream_explain`, renderer |
| `tests/test_explain.py` | **new** — see Acceptance Criteria |
| `tests/test_naming_regression.py` | **new** — snapshot of `_build_prompt` + `extract_name` behavior |
| `docs/QUICKSTART-WINDOWS-PE.md` | one row for `E` in the TUI key table |

# Approved Scope

Build is limited to the eight files above. Conventional commits, one
logical change per commit (expected: `refactor(core): extract
stream_generate` → `feat(core): explain prompt contract` → `feat(mcp):
explain_function tool` → `feat(tui): E-key explain mode` → `test: explain
+ naming regression`).

# Permitted Tools

pytest, ruff (changed files only), git local commits, python stdlib +
already-declared deps (httpx, textual). No network calls in tests —
httpx is monkeypatched.

# Prohibited Actions

- Pushing to any remote (per-occasion user authorisation required).
- Modifying `_SYSTEM`, `_build_prompt`, `extract_name`, or any existing
  MCP tool's signature/behavior.
- New dependencies of any kind.
- Touching `spectrida/verify/`, `spectrida/memory/` (pre-existing lint debt),
  `phantomrt`, or the workspace records (except the Final Report step).
- Writing to the `.i64` (v1 is strictly read-only analysis).

# Stop Conditions

Stop and report if: the `stream_generate` extraction cannot keep naming
output bit-identical; `DemoBackend`'s structure forces a facade redesign
beyond the file list; any existing test regresses; Ollama's response
format turns out to differ from the streaming assumptions in
`core/ollama.py` (would indicate unmodelled version drift).

# Acceptance Criteria

**Automated (my sandbox, must all pass):**

1. `tests/test_explain.py`:
   - prompt builder respects 80-insn cap and 4000-char pseudocode cap;
   - `parse_explanation` round-trips well-formed output;
   - parser survives: missing sections, lowercase headers, prose before
     `PURPOSE:`, garbage `CONFIDENCE` value → `unknown`;
   - mocked-transport streaming yields tokens in order and propagates
     `chunk["error"]` as `RuntimeError`;
   - DemoBackend stream produces a parseable explanation.
2. `tests/test_naming_regression.py`: `_build_prompt` byte-identical for
   pinned inputs; `extract_name` behavior pinned on 3 historical outputs.
3. Full suite: 35 existing + new tests, all green. Ruff clean on changed
   files.

**Live (user's machine — the 15% I cannot do):**

4. `spectrida --demo` → select a function → `E` → explanation streams.
5. On the Lesson-1 `target.exe` (32-bit PE): explanation of `factorial`
   mentions recursion; `add` identified as leaf arithmetic; `main`
   connected to `printf` via the format string.
6. Analyst-rated: ≥ 80% of explanations on 20 random functions judged
   "useful" (not merely plausible-sounding); latency ≤ 30 s/function on
   the 8B model.

# Required Evidence

- pytest output (full suite) pasted into the run record under `runs/`.
- Transcript or screenshot of criterion 5 output.
- Post-build: new episode record (per ep-2026-08-25-002's lesson —
  post-action review is not optional), `PROJECT_STATUS.md` `target_head`
  update, handoff refresh.

# Final Report

To be appended here by the build agent: commits produced, evidence
locations, deviations from this packet (with reasons), live-acceptance
table, and rollback confirmation (revert = drop the new module + binding;
no data migrations exist).

# Rollback

Additive-only design: revert the feature commits. The `ollama.py`
extraction is pinned by the regression snapshot, so a partial revert
(keep refactor, drop explain) is also safe.

# Risks

| Risk | Mitigation |
|---|---|
| Model ignores the output contract | Tolerant parser → degrade to raw text, never crash |
| Context bloat blows the token budget | Existing caps (80 insns / 8+8 neighbors / 10 strings) + 4000-char pseudocode tail |
| Explanation hallucination | Contract forces evidence citation + explicit CONFIDENCE; system prompt bans inventing behaviour |
| Refactor regresses naming | Snapshot test pins `_build_prompt`; extraction is payload-identical |
| 8B model too slow for TUI patience | Streaming render (perceived latency ≈ first token); 512-token hard cap |
