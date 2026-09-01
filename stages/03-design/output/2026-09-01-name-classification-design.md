# Design — tp-2026-09-01-006: three-state name classification in the agent loop

**Status:** approved by owner ("A", 2026-09-01)
**Trigger (live falsification):** first `agent_run` on BlackTie stopped in 5s with
"no unnamed functions remain", 0 LLM calls — TRUE under the old definition
(`_unnamed = startswith("sub_")`) but blind: the Lumina-resolved database has zero
`sub_*`; all 5,802 functions carry mangled CRT/thunk names. The loop could not say
WHY there was no work, and the report showed a bogus coverage delta (50.0 → 0.0).

## Decision

`classify_name(name)` replaces the boolean `_unnamed`:

- **unnamed** — empty or `sub_*`: the AI's work list.
- **library** — `j_*` thunks, MSVC-mangled (`?`), Itanium-mangled (`_ZN`): known
  library code. Never AI-renamed, never spends LLM budget, counted once per run
  and reported (`library_skipped`).
- **named** — anything else: already meaningful.

## Adjacent fixes in the same commit

- **Honest coverage:** `coverage_end` defaults to `coverage_start`; a no-work run
  now reports delta 0.0 instead of a fabricated collapse.
- **Stop-reason truthfulness:** "no unnamed functions remain" vs "all remaining
  functions processed" is decided by whether any *work items* existed
  (`report.items`), not by the seen-set (which now also holds library addresses).
- Stop reason names the library skip count when nonzero.

## Non-goals (recorded)

- Demangling library names for display: the `demangle` MCP tool already exists;
  the loop doesn't need prettier CRT names to do its job.
- Graph-vs-livedb coverage unification: baseline still reads the graph. Smell
  recorded in ep-2026-09-01-002; fixing it means deciding which source is
  authoritative for coverage — a separate decision.

## Acceptance

- 143/143 green incl. parametrized classifier tests, never-spend-LLM-on-library,
  all-library stop reason, honest zero-delta coverage.
- Live re-UAT: `agent_run` on the Lumina db must report
  `library_skipped ≈ 5800`, 0 LLM calls, truthful stop reason; then the stripped
  binary (WinLibs `strip` on target.exe) gives the loop real `sub_` victims.
