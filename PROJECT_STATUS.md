---
type: project-status
project: "spectrida-re-stack"
status: active
current_stage: 01-intake
execution_hold: true
build_approved: false
qa_approved: false
target_repo: "https://github.com/blackTieV2/spectrIDA-Reverse_Engineering_Stack"
approved_branch: "main"
approved_base: "c1c0570"
target_head: "UNRESOLVED — verify live"
working_tree_owner: ""
last_reviewed: "2026-08-25"
---

# PROJECT_STATUS — spectrIDA (blackTieV2 fork)

## What this project is

A personal fork of `ggfuchsi-oss/spectrIDA-Reverse_Engineering_Stack`:
parallel IDA Pro (idalib) binary analysis + local AI function naming
(Qwen3-8B via Ollama) + Neo4j knowledge graph + MCP server + phantomrt
dynamic layer (Unicorn/Frida/fuzzing).

## Current focus

Hardening the fork after an independent audit, and learning the tool on a
simple x86/x64 Windows PE target. This repository is also governed by the
model-neutral persistent workspace defined in `AGENTS.md`.

## Completed (user-authorised, 2026-08-25)

- fix(build): lz4/capstone/numpy declared as base dependencies
- fix(analysis): torch import guarded — CPU-only installs no longer
  silently return zero functions
- fix(analysis): 32-bit x86 PEs decode via CS_MODE_32 (was: 64-bit decoder)
- fix(analysis): Windows-hardcoded IDA/output paths replaced with
  platform-aware defaults
- chore: committed `desktop/node_modules` (7.3 MB, no source) removed;
  dev codegen scripts relocated to `scripts/dev/`

## Known issues (open)

- `spectrida/verify/` + `spectrida/memory/`: 229 pre-existing ruff errors;
  upstream CI lint step was already red. Not yet remediated (out of scope).
- Benchmark numbers in README are self-reported upstream; unverifiable
  without IDA Pro 9.x licence + the same hardware.
- `diaphora_*` MCP tools require a Diaphora checkout two levels above the
  package; undocumented upstream.
- phantomrt is alpha (0.1.x); treat verdicts as leads, not proof.

## Execution hold

**ACTIVE.** Consequential action (merge upstream, push to shared remotes,
release, dependency upgrades beyond the above) requires explicit user
approval. The 2026-08-25 hardening commits were explicitly authorised by
the user and are complete.

## Next safe action

Complete 01-intake: confirm target PE for the learning exercise
(x64 recommended; x86-32 now supported), confirm IDA Pro 9.x + idalib
availability on the operator machine, then approve a 04-build/05-qa run.
