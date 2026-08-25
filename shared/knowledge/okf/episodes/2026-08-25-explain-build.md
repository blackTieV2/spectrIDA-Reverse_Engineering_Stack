---
id: "ep-2026-08-25-003"
type: episode
title: "Explain mode built per tp-2026-08-25-001 (5 commits, 55 tests green)"
status: approved
authority: historical
project: "spectrida-re-stack"
stage: "04-build"
occurred_at: "2026-08-25"
tags: [build, explain, llm, tui, mcp]
relationships: ["tp-2026-08-25-001", "dec-2026-08-25-001"]
---

# Explain mode: prompt contract + MCP tool + TUI E-key, built and tested

- **When:** 2026-08-25
- **Stage / target:** 04-build / local master (commits c2e81eb..fd07670)
- **Trigger:** user approved build of tp-2026-08-25-001 ("Approved to proceed")
- **Observed state:** sandbox wiped between sessions twice — design packets
  lost once (never pushed), recovered from in-context text; WIP bundle
  snapshots now taken after every commit series
- **Actions taken:** transport refactor (snapshot-pinned), explain.py
  contract + tolerant parser, explain_function MCP tool (33rd), facade +
  both backends + TUI E-key, 20 new tests
- **Outcome:** 55/55 tests pass; ruff clean on changed files; naming path
  byte-identical post-refactor (pinned)
- **Validation:** pytest output; snapshot test; parser tolerance tests
  (garbage input → safe empty Explanation, never raises)
- **Failure / rollback:** confidence parser split on "-" broke on
  hyphenated garbage values ("absolutely-sure") — caught by tests, fixed
  to split on " - "; TUI line-buffer consumed the text before parsing —
  caught pre-commit by re-reading own diff; RichLog can't take
  token-level writes → line-buffered streaming
- **Lesson:** the tolerant parser is the feature. Models will violate any
  contract; the only question is whether the code degrades or dies.
- **Reusable?** yes — consolidation candidate: "structured LLM output =
  contract + tolerant parser + raw fallback", applies to agent loop
  (tp-2026-08-25-004)
- **Source evidence:** commits c2e81eb..fd07670; packet final report in
  stages/03-design/output/2026-08-25-explain-mode-design.md
