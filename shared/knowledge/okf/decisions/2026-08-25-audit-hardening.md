---
id: "dec-2026-08-25-001"
type: decision
title: "Apply audit-hardening fixes to the fork"
status: approved
authority: approved
project: "spectrida-re-stack"
decided_at: "2026-08-25"
decided_by: "user (blackTieV2)"
relationships: []
---

# Apply audit-hardening fixes to the fork

## Context

An independent audit of upstream (c1c0570) found: undeclared runtime
dependencies (lz4/capstone/numpy) breaking clean installs; an unguarded
torch import silently zeroing analysis results without the [gpu] extra;
32-bit x86 PEs decoded by the 64-bit Capstone decoder; Windows-only
hardcoded paths; a 7.3 MB committed node_modules tree with no source.

## Decision

Apply all five fixes to the fork; keep behavioural compatibility; add
regression tests; use Conventional Commits; do NOT take on the pre-existing
lint debt in `spectrida/verify/` and `spectrida/memory/` (bounded scope).

## Consequences

- Base `pip install spectrida` now yields a working analysis pipeline.
- 32-bit x86 PEs are genuinely supported (CS_MODE_32).
- Clone size drops ~7 MB.

## Rollback

`git revert` of the five commits listed in `okf/log.md` / git history.
