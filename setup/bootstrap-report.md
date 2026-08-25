# Bootstrap Report — spectrida-re-stack

- **Project name:** spectrIDA (blackTieV2 fork)
- **Project root:** this repository (operator convention:
  `%USERPROFILE%\Documents\GitHub\spectrIDA-Reverse_Engineering_Stack`)
- **Mode:** FRESH PROJECT MODE — confirmed for the *workspace layer*.
  The repository itself is an existing codebase; no pre-existing
  project-management/memory/governance files (AGENTS.md, PROJECT_STATUS.md,
  CONTEXT.md, stages/, runs/) existed, so no takeover conflict. No existing
  file was overwritten.
- **Date:** 2026-08-25
- **Specification:** model-neutral-persistent-agent-workspace v1.0

## Structure created

23 files across 3 directories: canonical root files
(AGENTS.md, CONTEXT.md, PROJECT_STATUS.md, workspace.manifest.yaml),
`_config/` policies, `model-adapters/`, `skills/`, `shared/` (tooling,
9 templates, OKF with domains/systems/datasets/decisions/episodes/
relationships/playbooks/references + 9 failure-pattern cards), `stages/`
00–06 with contracts, `runs/_template/`, `retrieval/` (schemas, evaluation
golden set, consolidation), workspace script stubs in `scripts/`,
`archive/README.md`.

`.runtime/recall/` exists locally and is gitignored (derived, rebuildable).

## Files skipped

- `.runtime/recall/*` — intentionally untracked (derived store).
- No vector database installed (per spec §23/§41).

## Unresolved facts

- `DEFAULT_TIMEZONE` — unresolved.
- `PROJECT_STATUS.md: target_head` — recorded as UNRESOLVED; verify live.

## Initial status

- current stage: 01-intake
- execution_hold: **true** (active; bootstrap does not grant approval)
- build_approved / qa_approved: false

## Retrieval backend status

Filesystem routing + exact + full-text + metadata + relationship awareness
(specified; index not yet built — `scripts/rebuild_recall_index.py` is a
documented stub).

## Semantic retrieval status

Not installed. Optional future stage, only after retrieval evaluation shows
value (spec §23).

## Deviations from spec v1.0

1. Workspace scripts are `.py` (cross-platform) rather than `.ps1`; the
   operator platform is Windows. Documented in `scripts/README.md`.
2. Workspace scripts live in the existing `scripts/` directory alongside
   pipeline scripts (spec layout), with `scripts/README.md` separating them.
3. The workspace was bootstrapped into an existing code repository rather
   than an empty directory — additive only, no overwrites.
4. README.md already existed (project documentation) and was kept; the
   workspace adds governance files beside it.

## Validation

- Structural: all canonical root files, 7 stage contracts, runtime
  templates, retrieval/evaluation structure — present.
- Instruction: authority hierarchy documented (`_config/authority-policy.yaml`);
  recall explicitly non-authoritative; execution hold explicit.
- Memory: five classes separated; frontmatter with provenance/status;
  supersession relationship types defined; promotion requires review.
- Security: no secrets written; `.runtime/` gitignored.
- Model neutrality: no vendor doctrine outside `model-adapters/`.
- All workspace YAML parses clean.

## Recommended first controlled run

`01-intake` for the x86/x64 Windows PE learning exercise: confirm the target
binary, confirm IDA Pro 9.x + idalib on the operator machine, record success
criteria in `stages/01-intake/output/`.
