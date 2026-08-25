---
id: "ep-2026-08-25-005"
type: episode
title: "tp-003 built: verified patching + backend portability NO-GO"
status: approved
authority: historical
project: "spectrida-re-stack"
stage: "04-build"
occurred_at: "2026-08-25"
tags: [build, patching, research, backend]
relationships: ["tp-2026-08-25-003", "ep-2026-08-25-001"]
---

# Verified patch pipeline + honest NO-GO on a free backend

- **When:** 2026-08-25
- **Stage / target:** 04-build / local master (a5506ce..5cd8e70)
- **Trigger:** user: "continue. whats next?" — proceeded to tp-003 in the
  approved order
- **Observed state:** codebase was read-only on bytes (only set_name /
  set_cmt); backend registry is format-level, idalib hard-wired into
  core/ida.py
- **Actions taken:** patchlog.py (write-ahead JSONL journal), worker
  commands (get_bytes/bits/patch), verified_patch orchestrator with
  auto-revert, revert_patch, facade + backend + 3 MCP tools (34-36);
  Part B spike enumerated the consumed idalib surface from live code and
  costed the three options
- **Outcome:** 71/71 tests pass; safety contract proven incl.
  read-back-mismatch auto-revert via a flaky-store fake
- **Validation:** pytest; the 0x06 mode-distinguisher test pins 32/64
  decode selection
- **Failure / rollback:** ruff unavailable (PyPI timeouts) — mitigated
  with compile + AST scan, recorded as deviation
- **Lesson:** the spike's real finding was where the cost lives — not the
  interface (facade is already type-clean) but the idalib-native shard
  MERGE and analysis-quality validation. Cheap answers come from
  enumerating the consumed surface, not from listing tool features.
- **Reusable?** yes — "enumerate the consumed surface before costing a
  port" (pairs with ep-004's "grep call sites before claiming a gap")
- **Source evidence:** commits a5506ce..5cd8e70;
  stages/02-research/output/backend-portability-report.md
