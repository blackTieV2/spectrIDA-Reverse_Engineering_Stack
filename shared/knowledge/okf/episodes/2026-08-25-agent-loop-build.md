---
id: ep-2026-08-25-006
title: tp-004 build — bounded agent loop
date: 2026-08-25
status: draft
related: [dec-2026-08-25-002, tp-2026-08-25-004]
---

# Episode: agent loop build

## What happened

Built the last and largest packet: `spectrida/agent/` (budget, planner,
memory, report, loop) plus MCP tools `agent_run`/`agent_status`. 94/94
tests green (23 new, scripted fake LLM).

## Decisions made (see dec-2026-08-25-002 for the full chain)

- In-process seams, not MCP-over-wire (#4).
- verify_decompilation stub → medium-confidence degrades to human queue (#5).
- Seen-set: each address processed once per run — tests caught the
  re-queue budget-waste bug before commit.
- OKF root from `SPECTRIDA_OKF_ROOT` / `[workspace] okf_root`; absent →
  run proceeds without workspace writes.

## Lessons

- Same lesson as 002a, caught earlier this time: **verify the seam's real
  behavior before building on it** — the packet assumed a working verifier;
  live code had a stub. The graceful-degradation design absorbed it.
- Tests earn their keep: the re-queue bug and the convergence-threshold
  mis-expectation (1% deltas over 3 iterations IS converged per spec) were
  both caught by the suite, not by review.

## State

- local HEAD: 7551889; origin/master: af34c66. Push pending device auth.
- Feature program complete. Next: push, then live acceptance on the user's
  machine, then protocol extraction (option D) as a follow-up packet if
  the loop's observed call pattern justifies it.
