# Episode — 2026-09-01 — the loop that truthfully had no work (tp-2026-09-01-006)

**Status:** draft (agent-authored, pending human approval)

## What happened

First live `agent_run` on BlackTie finished in 5 seconds: "no unnamed functions
remain", 0 LLM calls, coverage 50.0 → 0.0. Not a crash — a definitional bug the
live binary exposed: Lumina had resolved all 5,802 functions to mangled CRT/thunk
names, leaving zero `sub_*`. The loop's `_unnamed` filter was built for stripped
binaries; on a symbol-rich database it found no work and couldn't say why.

Diagnostics (agent_diag.py) confirmed: live db returns 5,802 functions, keys
correct, `unnamed by loop's filter: 0`, first names all `j_?…` mangled thunks.

## Fix (owner approved option A)

Three-state `classify_name`: unnamed / library / named (packet:
stages/03-design/output/2026-09-01-name-classification-design.md). Library code
never spends LLM budget; the report counts `library_skipped`; stop reasons
distinguish "no work existed" from "work finished"; coverage delta is honest
when nothing ran.

## Lesson

"Unnamed" is not a property of a name, it's a property of the *pipeline that
produced it*. Stripped binary → `sub_*`. Lumina binary → mangled symbols.
The classifier, not the string prefix, is the right seam.

## Test-first moment worth remembering

The first implementation double-counted library functions across iterations
(4 ≠ 2) because classification wasn't deduplicated through the seen-set —
caught immediately by `test_library_functions_never_spend_llm`. The test was
written from the design, the bug was in the build, the loop worked as intended.
