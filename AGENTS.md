# AGENTS.md — Canonical Agent Entry Point

**Project:** spectrIDA (blackTieV2 fork) — AI-assisted reverse-engineering stack.
**Spec:** model-neutral-persistent-agent-workspace v1.0
**Governing rule:** Recall may suggest. Authority decides. Live state verifies.

This file is the first thing any agent (any model, any vendor) reads. It is
canonical procedure. Everything else routes from here.

---

## 1. Filesystem authority

The filesystem is the durable source of truth. Chat history, model memory,
vector indexes, and recalled summaries are NOT authoritative. Machine indexes
(`.runtime/recall/`, Neo4j, embeddings) are derived, disposable, rebuildable.

## 2. Context loading order

1. `AGENTS.md` (this file)
2. `PROJECT_STATUS.md` — current truth
3. `CONTEXT.md` — stage router
4. `stages/<current-stage>/CONTEXT.md` — stage contract
5. Exact relevant references (never the whole tree)
6. Current run packet (`runs/<run-id>/`)

Do not load the whole workspace into context. Context is compiled, not accumulated.

## 3. Core operating rules

- **Current-profile-first.** `PROJECT_STATUS.md` outranks every historical record.
- **One stage per run.** A run belongs to exactly one stage in `stages/`.
- **Recon before change.** Read and verify the live target before modifying it.
- **Live-state verification.** Mutable facts (branch, HEAD, service state,
  approval) must be verified live. A remembered fact is not proof.
- **Dirty-tree protection.** Unexpected uncommitted work is someone else's
  preserved work. Recon read-only; never absorb or discard it silently.
- **Execution hold.** If `PROJECT_STATUS.md` says `execution_hold: true`,
  consequential action (build, merge, push, deploy, delete) is prohibited
  until the user explicitly lifts the hold.
- **Human approval gates.** Destructive, security-relevant, architectural,
  and release actions require explicit user approval. See
  `_config/authority-policy.yaml`.
- **Single writer.** One modifying agent per working tree. Other agents:
  read-only, or isolated worktrees/branches.
- **Bounded scope.** Do the approved task. Do not expand it. Scope-expansion
  is a named failure pattern — see
  `shared/knowledge/okf/playbooks/agent-failure-patterns/scope-expansion.md`.

## 4. Memory rules

- **Recall is never authority.** A semantic match, old handoff, or prior
  summary may suggest; only current verified state decides.
- **No secrets in memory.** Never write secrets to Markdown, YAML, task
  packets, indexes, logs, or prompts. See `_config/memory-policy.yaml`.
- **Promotion is deliberate.** Episodes and candidates never become canonical
  knowledge automatically. Promotion = propose → human review → promote.
  See `_config/memory-policy.yaml` §promotion.
- **Preserve evidence.** Do not delete or overwrite historical records; mark
  them superseded via `relationships:` frontmatter.

## 5. Model neutrality

This workspace must work for any model or vendor. Model-specific files live
only in `model-adapters/` as thin adapters and may never hold project truth.

## 6. Change control (Git)

Before modifying, run and record:

```text
git status
git branch --show-current
git rev-parse HEAD
```

Stage only files you created/changed for the task. Use Conventional Commits.
Do not push unless explicitly authorised.

## 7. When sources conflict

Do not silently reconcile. Identify the conflict, record both sources and
their authority levels (`_config/authority-policy.yaml`), prefer the
higher-authority source, verify mutable facts live, and escalate to the user
when the conflict affects consequential action.

## 8. Failure patterns

Before acting on anything recalled, skim
`shared/knowledge/okf/playbooks/agent-failure-patterns/index.md`. Those nine
cards are the known ways agents go wrong here.
