---
id: "tp-2026-08-25-002"
type: task-packet
title: "Dynamic→static feedback loop — Frida traces and fuzz verdicts annotate the graph, TUI, and OKF"
status: awaiting-build-approval
project: "spectrida-re-stack"
stage: "03-design"
created_at: "2026-08-25"
head_at_design: "f8ab962"
depends_on: []
---

# Task

Close the one-directional dynamic layer: today `live_trace` and `hunt_crashes`
*observe* the binary and return a verdict dict — then the knowledge
evaporates. This feature persists it:

1. **Graph annotations** — functions hit by a Frida trace / exercised by the
   fuzzer get durable properties (`dyn_executed`, `dyn_hit_count`,
   `dyn_last_verdict`, `dyn_last_run`).
2. **TUI surfacing** — a marker column in the function list and a detail
   line so the analyst sees "this function ran at runtime" at a glance.
3. **OKF failure cards** — every fuzz crash auto-writes a failure-pattern
   card into `shared/knowledge/okf/` so the workspace learns from dynamic
   evidence.

# Stage

03-design. This document is the only output. Build requires explicit user
approval.

# Current Verified State

Verified by live re-read at `f8ab962`:

- `spectrida/dynamic/live.py` — `live_trace(graph, tag, addresses,
  binary_path=None, ...)` (line 22) already receives the graph object and
  delegates to `atlas.analysis.frida_live.FridaLiveTarget`; RVA mapping via
  `rva_from_graph_addr` exists.
- `spectrida/dynamic/fuzz.py` — `hunt(graph, tag, addr, binary_path=None,
  ...)` (line 20), coverage-guided mutation loop.
- `spectrida/dynamic/annotate.py` — currently a stub surface:
  `annotator(graph)` (line 10). This is the designated seam for this
  feature.
- MCP tools `live_trace`, `hunt_crashes`, `dynamic_overview` return
  verdicts but persist nothing analyst-visible.
- Neo4j graph schema: `(:Function {binary, addr, name, size, ...})` —
  property additions are backward-compatible (Neo4j is schemaless).
- TUI function list widget: `spectrida/tui/widgets/funclist.py`.
- OKF failure-pattern cards: 9 examples already in
  `shared/knowledge/okf/` (seeded at workspace bootstrap); format proven.
- phantomrt is alpha (0.1.x) — verdicts are leads, not proof (recorded as
  known issue in PROJECT_STATUS.md).

# Read

1. `AGENTS.md` → `PROJECT_STATUS.md` → this packet
2. `spectrida/dynamic/annotate.py`, `live.py`, `fuzz.py` (all three are short)
3. `spectrida/mcp_server.py` — `live_trace`, `hunt_crashes` tool bodies
4. `spectrida/tui/widgets/funclist.py`
5. One existing failure-pattern card in `shared/knowledge/okf/` for format

# Relevant Prior Experience

> Historical hints only. Current verified target state controls execution.

- `ep-2026-08-25-001`: phantomrt claims were the least-verified part of the
  upstream README. → Every annotation written by this feature carries a
  `source: phantomrt-alpha` provenance property so future agents know the
  confidence class of what they're reading.
- `dec-2026-08-25-001`: additive-only changes; existing behavior pinned.
  → This feature adds graph properties and UI markers; it mutates no
  existing analysis path.

# Design

## 1. Annotation writer (`spectrida/dynamic/annotate.py`)

Grow the stub into the single writer for dynamic evidence:

```python
record_trace_hits(graph, binary, hits: list[TraceHit], run_id) -> int
record_fuzz_verdict(graph, binary, addr, verdict: FuzzVerdict, run_id) -> None
```

Both set properties on `(:Function)` nodes (MERGE on `(binary, addr)`),
append-only `run_id` for traceability, plus `source: "phantomrt-alpha"`.
All Cypher in this one module — the rest of the codebase never writes
dynamic properties directly.

## 2. Hook the producers

- `live.py::live_trace` → after the Frida session ends, call
  `record_trace_hits` with the observed hit list.
- `fuzz.py::hunt` → on each verdict, `record_fuzz_verdict`.
- MCP tools gain the count of annotated functions in their return dict
  (`"annotated": n`) — additive field, no signature change.

## 3. TUI surfacing

- `funclist.py`: marker column — `▶` executed, `✖` crash verdict,
  `?` needs_state. Markers read from the graph when available; absent graph
  → column blank (TUI must not require Neo4j).
- Browser screen detail line: "dynamic: executed 3×, last run 2026-08-25".

## 4. OKF failure cards from crashes

On `crash` verdict: write `shared/knowledge/okf/<date>-crash-<addr>.md`
using the existing card template — fields: target function, mutator seed
class, signal/exception, minimal repro seed path, static context (callers
from the graph). **Single-writer rule respected**: cards are written only
during a user-initiated run, never concurrently.

## Files touched (complete list)

| File | Change |
|---|---|
| `spectrida/dynamic/annotate.py` | grow stub into the annotation writer |
| `spectrida/dynamic/live.py` | call `record_trace_hits` post-session |
| `spectrida/dynamic/fuzz.py` | call `record_fuzz_verdict` per verdict |
| `spectrida/mcp_server.py` | additive `annotated` field in 2 tool returns |
| `spectrida/tui/widgets/funclist.py` | marker column |
| `spectrida/tui/screens/browser.py` | detail line |
| `spectrida/okf_bridge.py` | **new, small** — crash→failure-card writer |
| `tests/test_annotate.py` | **new** |
| `tests/test_okf_bridge.py` | **new** |

# Approved Scope

The nine files above. Commits (expected): `feat(dynamic): graph annotation
writer` → `feat(dynamic): wire trace/fuzz producers` → `feat(tui): dynamic
markers` → `feat(okf): failure cards from crash verdicts` → tests.

# Permitted Tools

pytest, ruff (changed files), git local commits, existing deps only
(neo4j driver already declared under `[graph]`).

# Prohibited Actions

- Pushing to any remote without per-occasion authorisation.
- Modifying phantomrt internals (`phantomrt/` subtree) — it is upstream
  alpha; we integrate at the `spectrida/dynamic/` seam only.
- Changing existing graph properties or any existing MCP tool signature.
- Writing to `.i64` databases (annotations live in the graph, not IDA).
- New dependencies.

# Stop Conditions

Stop if: Neo4j absence cannot be made graceful in the TUI (markers must
degrade silently); the graph object in `live.py`/`fuzz.py` turns out not
to expose a write session at the hook points (would force a redesign);
any phantomrt call signature differs from what `live.py` currently assumes.

# Acceptance Criteria

**Automated (sandbox):**

1. `test_annotate.py` — mocked graph: properties written with correct
   keys, provenance, run_id; idempotent re-annotation (MERGE semantics).
2. `test_okf_bridge.py` — crash verdict produces a card matching the
   template; no card written for `clean`/`needs_state` verdicts.
3. Full suite green; ruff clean on changed files.

**Live (user's machine):**

4. Frida-trace `target.exe`'s `main` → `factorial` shows `▶` in the TUI.
5. Fuzz a function with a crashing seed → card appears in OKF with the
   seed path and caller context.

# Required Evidence

- pytest output; `MATCH (f:Function) WHERE f.dyn_executed RETURN …`
  query result; the generated failure card; run record under `runs/`;
  episode record post-build.

# Final Report

To be appended by the build agent: commits, evidence, deviations,
rollback confirmation.

# Rollback

Additive-only: new graph properties and two new modules. Revert commits;
stale properties can be purged with one Cypher statement (documented in
the final report).

# Risks

| Risk | Mitigation |
|---|---|
| phantomrt alpha instability breaks the hook | Hooks wrapped in try/except — dynamic evidence is best-effort, never blocks a verdict return |
| Graph absent in TUI-only usage | Marker column degrades to blank; no hard dependency added |
| OKF card spam from fuzz loops | One card per (function, verdict-class) per run; dedupe by run_id |
| Provenance confusion (alpha verdicts read as fact) | Mandatory `source` property + PROJECT_STATUS known-issue already records the alpha caveat |
