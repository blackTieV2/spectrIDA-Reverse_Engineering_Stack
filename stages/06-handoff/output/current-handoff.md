# Current Handoff — 2026-08-25 (final, post feature program)

- **Current stage:** 05-qa — awaiting user-side live acceptance on the
  operator machine (IDA Pro 9.x + idalib + Ollama + Neo4j required)
- **Branch / HEAD:** `master` @ `68de72e` on
  `blackTieV2/spectrIDA-Reverse_Engineering_Stack` (verified live via
  ls-remote after push, 2026-08-25). One local-only bookkeeping commit
  (`077319f`, PROJECT_STATUS target_head) will ride the next push.
- **Dirty / live state:** working tree clean; nothing uncommitted; no stash
- **Active hold:** `execution_hold: true` — consequential actions
  (upstream merge, releases, dependency upgrades, force-push) require
  explicit user approval, per occasion
- **Approved actions:** read-only analysis; local commits on `master`;
  pushes explicitly authorised by the user per occasion
- **Prohibited actions:** secrets in any repo file or transcript;
  force-push/history rewrite; merging upstream without approval;
  agent-authored OKF records are draft-only until human-approved
- **Latest completed runs (all 2026-08-25, all user-authorised):**
  1. Hardening series (8 commits) — deps, torch guard, CS_MODE_32,
     portable paths, node_modules removal, gitignore anchor
  2. tp-001 Explain mode (prompt contract, tolerant parser, TUI E key)
  3. tp-002a Dynamic feedback (provenance, draft crash cards, markers)
  4. tp-003 Verified patching (journal, auto-revert) + backend NO-GO
  5. tp-004 Agent loop (`spectrida/agent/`, MCP agent_run/agent_status)
- **Tests:** 94/94 passing
- **Key decisions:** dec-2026-08-25-001 (adopt fork + hardening scope);
  dec-2026-08-25-002 (build chain, 002a revision, backend NO-GO,
  in-process seams, verify-stub degradation, budgets, draft-only memory)
- **Known issues:**
  - 229 pre-existing ruff errors in `spectrida/verify/` + `spectrida/memory/`
    (upstream CI lint was already red; out of scope, deliberately unfixed)
  - `verify_decompilation` is a stub — agent loop degrades
    medium-confidence names to the human queue (dec-2026-08-25-002 #5)
  - ruff not yet run on 002a/003/004 code (sandbox PyPI down; run on
    operator machine)
  - phantomrt is alpha (0.1.x); treat verdicts as leads, not proof
  - README benchmark numbers are upstream-self-reported; unverifiable
    without IDA Pro 9.x + identical hardware
  - `diaphora_*` MCP tools need a Diaphora checkout two levels above the
    package (undocumented upstream)
  - Historical secret-scan LOW hits in deleted `desktop/node_modules/`
    (@types/node `.d.ts` JSDoc placeholders) — false positives, no rotation
    needed
- **Next safe action:** user runs the six live-acceptance gates listed in
  PROJECT_STATUS.md "Next safe action", starting with `spectrida --demo`
- **Files the next agent should read:** AGENTS.md → PROJECT_STATUS.md →
  this file → shared/knowledge/okf/decisions/2026-08-25-agent-loop.md →
  stage CONTEXT.md

> Convenience summary only. PROJECT_STATUS.md and live state are authority.
