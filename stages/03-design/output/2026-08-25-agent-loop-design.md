---
id: "tp-2026-08-25-004"
type: task-packet
title: "Autonomous analysis agent — LLM drives the MCP toolset in a supervised convergence loop"
status: awaiting-build-approval
project: "spectrida-re-stack"
stage: "03-design"
created_at: "2026-08-25"
head_at_design: "f8ab962"
depends_on: ["tp-2026-08-25-001"]
---

# Task

Build the **agent loop**: an orchestrator that lets the LLM drive
spectrIDA's own 32 MCP tools autonomously — name a cluster of functions,
propagate meaning to callers, verify its own work, escalate what it can't
resolve — until a convergence condition or budget limit stops it.

This is the GhidraMCP *pattern* applied to our own stack, with two things
GhidraMCP doesn't have: (a) a workspace memory (`shared/knowledge/okf/`)
the agent reads for prior decisions and writes episodes into, and (b) the
Explain contract (`tp-2026-08-25-001`) as its reasoning substrate — the
agent doesn't just name, it *justifies*, and the justification is what a
human reviews.

**Explicit dependency:** this packet assumes Explain mode (`tp-2026-08-25-001`)
is built first. The agent's per-function step is literally "call
`explain_function`, act on the structured result."

# Stage

03-design. This document is the only output. Build requires explicit user
approval. This is the largest design of the four; expect the build phase
to produce sub-packets per milestone.

# Current Verified State

Verified by live re-read at `f8ab962`:

- 32 MCP tools exist (`mcp_server.py`, grep-counted) covering: analysis
  (`analyze_binary`, `poll_analysis`), context (`get_context`,
  `get_referenced_knowledge`), naming (`write_function_name`,
  `rename_function`, `baseline_naming`), verification
  (`verify_decompilation`, `scale_verify`), dynamics (`emulate_function`,
  `hunt_crashes`, `live_trace`), and Diaphora interop.
- `verify_decompilation` + `scale_verify` already exist — the loop's
  self-check step reuses them rather than inventing a new validator.
- `baseline_naming` measures named-vs-`sub_*` coverage — a ready-made
  convergence metric.
- OKF: decision records and episodes already accumulate
  (`dec-2026-08-25-001`, `ep-…-001`, `ep-…-002`); the format supports
  agent-authored records (authority field distinguishes them:
  agent-authored records are `status: draft` until human-approved).
- Naming path (`core/ollama.py`, `api.py::batch_name`) is single-shot,
  no memory, no verification. The loop wraps, not modifies, this path.
- No orchestration code exists anywhere in the tree (grep-verified).

# Read

1. `AGENTS.md` → `PROJECT_STATUS.md` → this packet
2. `tp-2026-08-25-001` (Explain mode design) — the dependency
3. `spectrida/mcp_server.py` — tool list and the `baseline_naming`,
   `write_function_name`, `verify_decompilation` bodies
4. `shared/knowledge/okf/decisions/2026-08-25-audit-hardening.md` (decision
   record format) and one failure-pattern card
5. `runs/_template/` (run-state format the loop must emit)

# Relevant Prior Experience

> Historical hints only. Current verified target state controls execution.

- `ep-2026-08-25-001`: the model names generic helpers well and whiffs on
  domain logic. → The loop's escalation rule: low-confidence explanations
  go to a human queue *instead of* being renamed — the agent's job is to
  know what it doesn't know.
- `ep-2026-08-25-002`: post-action review caught real gaps. → The loop
  itself has a mandatory review artifact: every run ends with a
  human-reviewable diff report, and nothing auto-applies above the
  confidence threshold.
- Workspace doctrine (single-writer rule): the agent holds a run-scoped
  write lock on OKF; concurrent agent runs are prohibited.

# Design

## 1. Architecture (`spectrida/agent/`, new subpackage)

```
spectrida/agent/
├── __init__.py
├── loop.py        # the convergence loop
├── planner.py     # picks the next unit of work
├── memory.py      # OKF read/write (few-shot decisions, episode drafts)
├── budget.py      # token/time/action limits, hard stops
└── report.py      # end-of-run diff report
```

The loop is **not** an MCP client calling the MCP server over the wire —
it imports and calls the same underlying functions directly (in-process),
avoiding a network hop and making the whole thing unit-testable. The MCP
server remains the external interface; the agent is an internal consumer
of the same library code.

## 2. The loop

```
run(binary, goal, budget):
    state = load run-state (runs/<id>/run-state.yaml)
    while not converged(state) and budget.remaining():
        unit   = planner.next(state)          # a function cluster
        expl   = explain_function(unit)       # tp-…-001, structured
        if expl.confidence == "low":
            human_queue.append(unit); continue
        rename via write_function_name(expl.suggested_name)
        verify_decompilation(unit)            # self-check
        memory.log_draft_episode(unit, expl)  # draft, not approved
        state.coverage = baseline_naming()    # convergence metric
    report.emit(state)                        # human-reviewable diff
```

**Convergence:** coverage delta < 2% over 3 consecutive iterations, OR
planner returns no eligible units, OR budget exhausted.

## 3. Supervision model (the part that makes this safe)

- **Thresholds**: auto-apply only `high` confidence; `medium` requires the
  suggested name to survive `verify_decompilation`; `low` → human queue.
- **Budget**: hard caps on LLM calls, wall time, and renames per run
  (defaults: 200 / 30 min / 100). Budget exhaustion is a clean stop, not
  an error.
- **Human queue**: `runs/<id>/review-queue.md` — every skipped or
  low-confidence unit with its explanation, so review is a reading task,
  not an archaeology task.
- **Draft-only memory**: agent writes OKF records as `status: draft`;
  promotion requires the human (existing memory-promotion-review template).

## 4. OKF as few-shot memory

Before naming a cluster, `memory.py` pulls the N most similar approved
decisions/episodes (same binary family, similar call shape) into the
prompt prefix. v1 similarity = shared caller names + string overlap;
embedding retrieval is a follow-up, not v1.

## 5. MCP surface

Two new tools: `agent_run(binary, goal, budget_json) -> {run_id}` (async
job, reusing the existing job pattern from `analyze_binary`) and
`agent_status(run_id)`. The TUI gets a read-only run monitor (follow-up
packet; not v1).

## Files touched (complete list)

| File | Change |
|---|---|
| `spectrida/agent/*` | **new subpackage** (5 modules above) |
| `spectrida/mcp_server.py` | `agent_run`, `agent_status` |
| `tests/test_agent_loop.py` | **new** — mocked LLM, convergence, budget, escalation |
| `tests/test_agent_memory.py` | **new** — OKF draft writes, few-shot retrieval |
| `shared/knowledge/okf/` | receives draft records at runtime only (no committed changes) |

# Approved Scope

The files above. Commits (expected): `feat(agent): loop skeleton with
budget + convergence` → `feat(agent): OKF memory (draft-only)` →
`feat(agent): planner + escalation queue` → `feat(mcp): agent_run /
agent_status` → `test: agent loop`.

# Permitted Tools

pytest, ruff (changed files), git local commits, existing deps. Tests use
a scripted fake LLM (deterministic response script) — no live Ollama in CI
or sandbox.

# Prohibited Actions

- Pushing without per-occasion authorisation.
- Auto-approving agent-authored OKF records (draft-only is the doctrine).
- Modifying existing naming/verification tool behavior.
- Concurrent agent runs (single-writer rule).
- Live-LLM tests in the test suite.
- New dependencies without explicit approval.

# Stop Conditions

Stop if: the in-process reuse of MCP tool bodies turns out to be
impossible without refactoring `mcp_server.py`'s module-level state (then
design a thin service layer first — report before doing it); the
convergence metric proves unstable on real binaries; Explain mode
(`tp-…-001`) acceptance is not met (dependency unmet — do not start).

# Acceptance Criteria

**Automated (sandbox):**

1. Scripted-LLM loop run converges on a fixture call-graph; budget
   exhaustion stops cleanly mid-run; low-confidence units land in the
   review queue, never renamed.
2. Memory: draft records written, none auto-approved; few-shot retrieval
   returns relevant prior decisions for a fixture query.
3. Full suite green; ruff clean on changed files.

**Live (user's machine):**

4. On `target.exe`: agent run names `add`/`factorial`/`compute` correctly
   (ground truth known), escalates nothing, finishes within budget.
5. On a real mid-size binary: ≥ 50% coverage improvement over
   `baseline_naming`, zero renames the human reviewer marks "wrong" in the
   review queue sample (plausible-but-wrong is the metric that matters).

# Required Evidence

- pytest output; a full run-state YAML; the end-of-run diff report; the
  review queue; episode record post-build; `PROJECT_STATUS.md` +
  handoff update.

# Final Report

To be appended by the build agent: commits, evidence, deviations, and an
honest account of where the agent was confident-but-wrong (that's the
number that decides whether this feature graduates from supervised to
autonomous-by-default in some future version — current design is
supervised, always).

# Rollback

New subpackage + two MCP tools; revert commits. Runtime draft records in
OKF are inert until approved; a purge script ships with the feature.

# Risks

| Risk | Mitigation |
|---|---|
| Confident-but-wrong renames at scale | Thresholds + verify_decompilation gate + review queue; metric 5 measures exactly this |
| LLM loop burns tokens/time unbounded | Hard budget caps, clean-stop semantics |
| Agent writes pollute workspace memory | Draft-only authority; single-writer lock; purge script |
| MCP module state makes in-process reuse hard | Stop condition #1 surfaces it early; service-layer redesign reported before built |
| Scope is genuinely large | Milestones as sub-packets at build time; skeleton loop lands first and is useful alone |

---

## Final Report — 2026-08-25 (built)

**Status: BUILT.** Commits 6f56c01..7551889 on top of 7989370.

### Deviations from this packet (all logged)

1. **verify_decompilation is a stub.** Pre-build live-state check found the
   medium-confidence gate's verifier returns `ready_for_verification` only.
   Handled per dec-2026-08-25-002 #5: stub responses degrade to the human
   queue with `verify_note = "verify_decompilation stub"`. A real verifier
   returning `verified: true` upgrades items without any loop change —
   test-pinned (`test_real_verifier_would_upgrade`).
2. **Seen-set added.** Tests caught the loop re-explaining and re-queueing
   the same queued functions every iteration, wasting LLM budget. Each
   address is now processed exactly once per run; the loop terminates via
   "all remaining functions processed" in the common case. The convergence
   detector remains for multi-pass scenarios and is unit-pinned directly.
3. **OKF root via config/env** (`SPECTRIDA_OKF_ROOT` or `[workspace]
   okf_root`) — config has no `workspace_root` helper. Absent config, the
   run works but writes no workspace records (report still returned via
   `agent_status`).
4. **ruff unavailable again (PyPI timeouts).** Mitigated with py_compile +
   AST unused-import scan, as in tp-003. Deviation carried.

### Test evidence

- 23 new tests in tests/test_agent.py — scripted fake LLM, no Ollama/IDA/
  Neo4j anywhere in the suite.
- **94/94 passing** (71 pre-existing + 23 new).
- Proven: caps fire on all three dimensions; thresholds route correctly;
  stub degradation; budget exhaustion is a normal exit with the cap named;
  failed explains terminate cleanly; draft memory dedupes and never raises;
  convergence detector semantics.

### Program status

All four packets (001, 002a, 003, 004) are now BUILT. Push of 003+004
commits is pending user device authorization.
