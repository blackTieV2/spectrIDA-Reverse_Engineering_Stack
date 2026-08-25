# Current Handoff — 2026-08-25

- **Current stage:** 01-intake (learning exercise: first x86 Windows PE)
- **Current target:** user-selected simple x86 (32-bit) Windows PE — TBD by user
- **Branch / HEAD / system version:** `master` @ `31924b6` (verified live on
  `origin/master` via GitHub API, 2026-08-25; superseded only by the
  housekeeping commit that adds this file — verify live)
- **Dirty / live state:** working tree clean; nothing uncommitted; no stash
- **Active hold:** `execution_hold: true` — consequential actions (upstream
  merge, releases, dependency upgrades, force-push) require explicit user
  approval
- **Approved actions:** read-only analysis; local commits on `master`;
  pushes explicitly authorised by the user per occasion
- **Prohibited actions:** secrets in any repo file or transcript;
  force-push/history rewrite; merging upstream without approval
- **Latest completed run:** 2026-08-25 hardening series (8 commits,
  `0e06873..31924b6`), pushed to `blackTieV2/spectrIDA-Reverse_Engineering_Stack`
- **Latest commit:** `31924b6` — fix: correct approved_branch to master in
  project status
- **Key decisions:** dec-2026-08-25-001 (adopt fork + hardening scope)
- **Known issues:**
  - 229 pre-existing ruff errors in `spectrida/verify/` + `spectrida/memory/`
    (upstream CI lint was already red; out of scope, deliberately unfixed)
  - phantomrt is alpha (0.1.x); its test deps (torchdiffeq, tqdm) were not
    exercised in the audit sandbox
  - README benchmark numbers are upstream-self-reported; unverifiable
    without IDA Pro 9.x + identical hardware
  - `diaphora_*` MCP tools need a Diaphora checkout two levels above the
    package (undocumented upstream)
  - Historical secret-scan LOW hits in deleted `desktop/node_modules/`
    (@types/node `.d.ts` JSDoc placeholders) — false positives, no rotation
    needed
- **Next safe action:** complete 01-intake — user picks/compiles a simple
  x86 PE, confirms IDA Pro 9.x + idalib on their machine, follows
  `docs/QUICKSTART-WINDOWS-PE.md` (Step 0 workspace already exists here)
- **Files the next agent should read:** AGENTS.md → PROJECT_STATUS.md →
  CONTEXT.md → stage CONTEXT.md

> Convenience summary only. Below PROJECT_STATUS.md and live state in authority.
