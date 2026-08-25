---
id: "ep-2026-08-25-004"
type: episode
title: "tp-002 scope falsified by live state; revised 002a built"
status: approved
authority: historical
project: "spectrida-re-stack"
stage: "04-build"
occurred_at: "2026-08-25"
tags: [build, dynamic, doctrine, scope-revision]
relationships: ["tp-2026-08-25-002", "ep-2026-08-25-001"]
---

# Design packet contradicted by live code; stop-condition fired; reduced scope built

- **When:** 2026-08-25
- **Stage / target:** 04-build / local master (commits 3cbe4fe..5d3eeb2)
- **Trigger:** user approved build of tp-002 (dynamic→static feedback)
- **Observed state:** the packet's core premise ("verdicts evaporate;
  nothing persists") was wrong — `hunt_crashes` and `live_trace` MCP tools
  already annotate the graph via `annotator()`, and `dynamic_overview`
  already reads the annotations back
- **Actions taken:** stopped per the packet's own stop condition ("live
  state contradicts the task packet"); verified the true gaps by grep
  (TUI markers absent, OKF bridge absent, provenance absent); revised to
  002a with the user; built only the genuine gaps
- **Outcome:** 2 commits; 63/63 tests pass; compile + import scan clean
- **Validation:** pytest; packet final report with deviation list
- **Failure / rollback:** design was written from a partial read (only
  `annotate.py`'s stub, not the MCP tool bodies that already call it).
  Rollback: revert 5d3eeb2.
- **Lesson:** "Read the seam, not the stub." The stub file looked empty,
  so the design assumed the capability was absent — but the *callers*
  (MCP tools) were already doing the work. For integration designs,
  grep the call sites, not just the module.
- **Reusable?** yes — consolidation candidate: "integration design =
  grep call sites before claiming a gap" (pairs with ep-001's lesson)
- **Source evidence:** commits 3cbe4fe, 5d3eeb2; packet
  stages/03-design/output/2026-08-25-dynamic-feedback-design.md
