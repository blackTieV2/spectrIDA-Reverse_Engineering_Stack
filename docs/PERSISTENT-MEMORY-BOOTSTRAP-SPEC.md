# Persistent Memory Workspace — Bootstrap Specification (v1.0)

> Source document supplied by the project owner on 2026-08-25. The workspace
> it describes is instantiated at the root of this repository. This file is
> the canonical bootstrap spec — run it once per project, not per session.
> Routine work uses the much smaller `AGENTS.md + PROJECT_STATUS.md + stage
> CONTEXT.md + compiled task packet` path.

---

Yes. The prompt below is the version I would now use for a **brand-new project**.

It deliberately goes beyond the earlier bootstrap prompt. It tells the agent not only **what folders/files to create**, but **why each memory layer exists, what authority it has, how information moves between layers, how recall must be governed, and how future agents are expected to use the system**.

The critical design principle throughout is:

> **Recall may suggest. Authority decides. Live state verifies.**

---

# MODEL-GENERIC FRESH PROJECT PERSISTENT MEMORY, CONTEXT, AND AGENT WORKSPACE BOOTSTRAP PROMPT

````markdown
# MODEL-GENERIC FRESH PROJECT PERSISTENT MEMORY, CONTEXT, AND AGENT WORKSPACE BOOTSTRAP

You are the bootstrap and architecture agent for a NEW project.

Your task is to create and populate a complete, persistent, model-neutral project workspace that can be safely used by future AI agents, humans, coding assistants, local models, cloud models, or orchestration systems.

This is not merely a folder-generation task.

You are creating the project's:

- persistent memory;
- current-state ledger;
- durable knowledge system;
- episodic experience store;
- procedural instruction system;
- runtime checkpoint system;
- context-routing system;
- retrieval and recall architecture;
- authority model;
- stage workflow;
- human approval gates;
- future-agent handoff mechanism;
- retrieval feedback system;
- candidate knowledge-consolidation process;
- evaluation framework.

The result must remain understandable and usable even if the current AI model, agent framework, vector database, embedding model, MCP implementation, or orchestration software is replaced later.

The filesystem is the durable human-readable foundation.

Git should provide change history when the workspace is version controlled.

Machine indexes, vector databases, embeddings, caches, and runtime stores are DERIVED systems and must never become the sole source of project truth.

---

# 1. VARIABLES

Resolve these before proceeding.

```text
PROJECT_NAME={{PROJECT_NAME}}
PROJECT_SLUG={{PROJECT_SLUG}}
PROJECT_ROOT={{PROJECT_ROOT}}
TARGET_REPOSITORY={{TARGET_REPOSITORY_OR_NONE}}
WORKSPACE_ROOT={{WORKSPACE_ROOT_OR_PROJECT_ROOT}}
DEFAULT_TIMEZONE={{TIMEZONE_OR_UNKNOWN}}
INITIAL_USER_GOAL={{INITIAL_USER_GOAL_OR_UNKNOWN}}
````

If a value is not known:

* do not invent it;
* record it as unresolved;
* create the structure anyway where safe;
* put the missing item into the project status and intake records.

---

# 2. MODE

This prompt is for:

FRESH PROJECT MODE.

Before creating anything, inspect `PROJECT_ROOT`.

If meaningful project-management, memory, agent-governance, or existing workspace files already exist, STOP.

Do not overwrite them.

Report:

```text
FRESH PROJECT MODE NOT CONFIRMED
TAKEOVER / EXISTING PROJECT AUDIT REQUIRED
```

This prompt must not be used to destructively restructure an existing project.

---

# 3. PURPOSE OF THE SYSTEM

Future agents will operate under several constraints:

1. AI context windows are finite.
2. Chat history is not a reliable project database.
3. Models can be changed.
4. Agents may misunderstand old summaries as current truth.
5. Semantic similarity does not prove authority.
6. Old branches, paths, configurations, or project decisions may become stale.
7. Raw transcripts contain useful information mixed with noise and mistakes.
8. Runtime execution state is different from durable knowledge.
9. Human operators must be able to understand and repair the system without an AI model.
10. A future agent must be able to resume a project without loading the complete historical conversation.

The workspace must therefore separate:

```text
CURRENT TRUTH
from
DURABLE KNOWLEDGE
from
PAST EXPERIENCE
from
OPERATING RULES
from
ACTIVE RUN STATE
from
DERIVED RETRIEVAL INDEXES
```

Do not collapse these into one "memory" folder.

---

# 4. FUNDAMENTAL ARCHITECTURAL RULE

The system must implement this hierarchy:

```text
                USER AUTHORITY
                      │
                      ▼
             VERIFIED LIVE STATE
                      │
                      ▼
             CURRENT PROJECT PROFILE
                      │
                      ▼
             CANONICAL INSTRUCTIONS
                      │
                      ▼
          APPROVED DESIGNS / KNOWLEDGE
                      │
                      ▼
             HISTORICAL EXPERIENCE
                      │
                      ▼
              RETRIEVAL / RECALL
```

The governing rule is:

> Recall may suggest. Authority decides. Live state verifies.

No recalled memory, semantic search result, embedding match, old handoff, previous prompt, historical note, or model-generated summary may silently override current verified truth.

---

# 5. AUTHORITY ORDER

Create an explicit authority policy using this default order:

1. Explicit current user instruction.
2. Verified live target state from the current run.
3. Current `PROJECT_STATUS.md` or equivalent current system profile.
4. Canonical `AGENTS.md`, root `CONTEXT.md`, and selected stage contract.
5. Approved design, architecture, decision, and change-control records.
6. Current approved durable knowledge.
7. Current approved handoff.
8. Historical episodic records and previous run evidence.
9. Previous prompts, conversations, summaries, and superseded handoffs.
10. Semantic, vector, or associative retrieval results.

When sources conflict:

* do not silently reconcile them;
* identify the conflict;
* record both sources;
* determine their authority levels;
* prefer the higher-authority source;
* require live verification for mutable operational facts;
* escalate to the user where the conflict affects consequential action.

---

# 6. MEMORY MODEL

Create five clearly separated memory classes.

## 6.1 Current-State Profile

Purpose:

Represent the latest consolidated state of the project.

Primary file:

```text
PROJECT_STATUS.md
```

This file should answer:

* What project is this?
* What stage are we in?
* What target is being worked on?
* What is currently approved?
* What is currently prohibited?
* Is an execution hold active?
* What branch or system state is expected?
* What major decisions are current?
* What risks are known?
* What was the latest checkpoint?
* What is the exact next safe action?

The current profile is concise.

It is not a historical log.

Historical detail belongs elsewhere.

---

## 6.2 Semantic Memory

Purpose:

Store durable facts, concepts, architecture, schemas, policies, domain knowledge, validated technical understanding, and reusable knowledge.

Default location:

```text
shared/knowledge/okf/
```

Examples:

* architecture concepts;
* model policy;
* system design;
* network topology concepts;
* business rules;
* terminology;
* approved technical conclusions;
* data schemas;
* reusable lessons.

Semantic knowledge must normally include YAML frontmatter containing provenance and status.

---

## 6.3 Episodic Memory

Purpose:

Store what happened.

Examples:

* project changes;
* failed attempts;
* incidents;
* dirty-tree discoveries;
* deployment outcomes;
* previous model tests;
* previous troubleshooting episodes;
* important operator interventions;
* unexpected tool behaviour;
* rollback outcomes.

Episodic memory answers:

> What happened last time we encountered something like this?

It must not automatically become current truth.

---

## 6.4 Procedural Memory

Purpose:

Store how agents and humans should behave.

Examples:

* `AGENTS.md`;
* `CONTEXT.md`;
* stage contracts;
* runbooks;
* playbooks;
* operating rules;
* tool policies;
* approval rules;
* change-control doctrine;
* safety boundaries.

Procedural memory must be model-neutral.

A future agent may propose changes to procedural memory but must not silently rewrite canonical procedures.

---

## 6.5 Runtime / Thread Memory

Purpose:

Record the state of an ACTIVE workflow.

Default location:

```text
runs/<run-id>/
```

Runtime memory records:

* current stage;
* current step;
* completed steps;
* pending steps;
* approvals;
* model;
* target;
* branch or system state;
* input hashes;
* output hashes;
* rollback reference;
* failure state;
* resume instruction.

Runtime memory is not durable project truth.

It exists so an interrupted agent can resume safely.

---

# 7. PROFILE VERSUS COLLECTION RULE

Use this hybrid pattern:

```text
PROFILE
= concise latest state

COLLECTION
= detailed knowledge, history, evidence, experience
```

Read order:

1. Current profile.
2. Canonical instructions.
3. Selected stage contract.
4. Relevant durable collection records.
5. Current run state.
6. Derived retrieval results.

An old collection item must never silently override the current profile.

---

# 8. REQUIRED PROJECT STRUCTURE

Create the following structure.

Use lowercase-with-hyphens for ordinary files and directories.

Keep canonical uppercase root filenames exactly as shown.

```text
PROJECT_ROOT/
│
├── AGENTS.md
├── CONTEXT.md
├── PROJECT_STATUS.md
├── README.md
├── workspace.manifest.yaml
│
├── setup/
│   ├── README.md
│   └── bootstrap-report.md
│
├── _config/
│   ├── README.md
│   ├── memory-policy.yaml
│   ├── retrieval-policy.yaml
│   ├── authority-policy.yaml
│   └── tool-profiles.yaml
│
├── model-adapters/
│   └── README.md
│
├── skills/
│   └── README.md
│
├── shared/
│   │
│   ├── tooling/
│   │   └── README.md
│   │
│   ├── templates/
│   │   ├── knowledge-record.template.md
│   │   ├── episodic-record.template.md
│   │   ├── decision-record.template.md
│   │   ├── run-state.template.yaml
│   │   ├── context-manifest.template.yaml
│   │   ├── task-packet.template.md
│   │   ├── memory-promotion-review.template.md
│   │   ├── retrieval-feedback.template.yaml
│   │   └── current-handoff.template.md
│   │
│   └── knowledge/
│       └── okf/
│           ├── index.md
│           ├── log.md
│           │
│           ├── domains/
│           │   └── index.md
│           │
│           ├── systems/
│           │   └── index.md
│           │
│           ├── datasets/
│           │   └── index.md
│           │
│           ├── decisions/
│           │   └── index.md
│           │
│           ├── episodes/
│           │   └── index.md
│           │
│           ├── relationships/
│           │   └── index.md
│           │
│           ├── playbooks/
│           │   ├── index.md
│           │   └── agent-failure-patterns/
│           │       ├── index.md
│           │       ├── stale-branch-or-dead-base.md
│           │       ├── dirty-tree-collision.md
│           │       ├── wrong-target.md
│           │       ├── execution-hold-violation.md
│           │       ├── stale-handoff-conflict.md
│           │       ├── multiple-agents-one-working-tree.md
│           │       ├── scope-expansion.md
│           │       ├── false-completion-claim.md
│           │       └── live-state-not-verified.md
│           │
│           └── references/
│               └── index.md
│
├── stages/
│   ├── 00-triage/
│   │   ├── CONTEXT.md
│   │   ├── references/
│   │   └── output/
│   │
│   ├── 01-intake/
│   │   ├── CONTEXT.md
│   │   ├── references/
│   │   └── output/
│   │
│   ├── 02-research/
│   │   ├── CONTEXT.md
│   │   ├── references/
│   │   └── output/
│   │
│   ├── 03-design/
│   │   ├── CONTEXT.md
│   │   ├── references/
│   │   └── output/
│   │
│   ├── 04-build/
│   │   ├── CONTEXT.md
│   │   ├── references/
│   │   └── output/
│   │
│   ├── 05-qa/
│   │   ├── CONTEXT.md
│   │   ├── references/
│   │   └── output/
│   │
│   └── 06-handoff/
│       ├── CONTEXT.md
│       ├── references/
│       └── output/
│           └── current-handoff.md
│
├── runs/
│   ├── README.md
│   └── _template/
│       ├── run-state.yaml
│       ├── context-manifest.yaml
│       ├── task-packet.md
│       ├── retrieval-feedback.yaml
│       └── memory-promotion-review.md
│
├── retrieval/
│   ├── README.md
│   ├── schemas/
│   │   ├── memory-record.schema.yaml
│   │   ├── relationship.schema.yaml
│   │   └── retrieval-event.schema.yaml
│   ├── evaluation/
│   │   ├── README.md
│   │   ├── golden-set.yaml
│   │   ├── expected-results.yaml
│   │   └── scoring.md
│   └── consolidation/
│       ├── README.md
│       └── candidates/
│
├── scripts/
│   ├── README.md
│   ├── new-controlled-run.*
│   ├── compile-agent-context.*
│   ├── verify-target-state.*
│   ├── rebuild-recall-index.*
│   ├── search-recall-memory.*
│   ├── verify-recall-authority.*
│   ├── record-retrieval-feedback.*
│   ├── propose-memory-consolidation.*
│   └── test-recall-system.*
│
├── .runtime/
│   └── recall/
│
└── archive/
    └── README.md
```

Use the appropriate script extension for the local platform.

If executable scripts are not yet appropriate, create well-documented stubs specifying their interface and intended behaviour.

---

# 9. ROOT FILE RESPONSIBILITIES

## AGENTS.md

Create the canonical model-neutral agent entry point.

It must state:

* filesystem authority;
* context loading order;
* one-stage-per-run rule;
* current-profile-first rule;
* recon-before-change rule;
* dirty-tree protection;
* execution-hold behaviour;
* human approval gates;
* single-writer rule;
* model neutrality;
* memory-promotion rules;
* retrieval limitations;
* live-state verification;
* prohibition on treating recall as authority;
* prohibition on secrets in memory;
* requirement to preserve evidence.

Recommended loading order:

```text
1. AGENTS.md
2. PROJECT_STATUS.md
3. CONTEXT.md
4. selected stage CONTEXT.md
5. exact relevant references
6. current run packet
```

---

## CONTEXT.md

Create a concise router.

It must explain which stage applies to which kind of task.

Do not put all project knowledge into this file.

Its purpose is routing, not storage.

---

## PROJECT_STATUS.md

Populate the initial current-state ledger.

Include frontmatter such as:

```yaml
type: project-status
project: "<project slug>"
status: active
current_stage: 00-triage
execution_hold: true
build_approved: false
qa_approved: false
target_repo: ""
approved_branch: ""
approved_base: ""
target_head: ""
working_tree_owner: ""
last_reviewed: ""
```

The initial execution hold should remain active until the project has completed enough intake/recon/design for consequential action to be explicitly approved.

---

## workspace.manifest.yaml

Record:

```yaml
workspace:
  name: ""
  slug: ""
  specification:
    name: model-neutral-persistent-agent-workspace
    version: "1.0"
    installed_at: ""
    last_audited: ""

  canonical_files:
    agent_entrypoint: AGENTS.md
    router: CONTEXT.md
    status: PROJECT_STATUS.md

  memory:
    current_profile: PROJECT_STATUS.md
    durable_root: shared/knowledge/okf
    episodic_root: shared/knowledge/okf/episodes
    runtime_root: runs
    derived_recall_root: .runtime/recall

  stages:
    - 00-triage
    - 01-intake
    - 02-research
    - 03-design
    - 04-build
    - 05-qa
    - 06-handoff

  model_specific_files_are_adapters_only: true
  vector_index_is_authoritative: false
```

---

# 10. STAGE MODEL

Create seven stage contracts.

## 00-triage

Purpose:

* understand request;
* classify risk;
* select mode;
* identify target;
* decide whether recon is required.

No implementation.

---

## 01-intake

Purpose:

* establish project goal;
* constraints;
* stakeholders;
* success criteria;
* target repository/system;
* unresolved requirements.

No implementation unless explicitly approved.

---

## 02-research

Purpose:

* gather evidence;
* perform read-only recon;
* inspect source material;
* validate assumptions;
* identify prior relevant experience.

Research output is evidence, not automatic approval.

---

## 03-design

Purpose:

* convert approved requirements and evidence into an implementation design;
* define scope;
* define acceptance criteria;
* identify rollback;
* identify risks.

Design does not itself authorise build.

---

## 04-build

Purpose:

Implement only the approved design and scope.

Requires:

* verified live target;
* applicable target gate;
* explicit build approval;
* execution hold clear;
* working-tree ownership clear.

---

## 05-qa

Purpose:

Validate the deliverable.

QA must not silently become another build phase unless remediation is explicitly permitted.

---

## 06-handoff

Purpose:

Consolidate:

* current state;
* completed work;
* evidence;
* decisions;
* unresolved issues;
* current target;
* next safe action.

The handoff should allow a fresh human or AI supervisor to continue without the complete previous conversation.

---

# 11. CONTEXT ENGINEERING

Do not build routine agent prompts by accumulating the whole project history.

Runtime context must be COMPILED.

The preferred runtime pattern is:

```text
canonical doctrine
+ current profile
+ selected stage contract
+ verified live state
+ approved scope
+ relevant references
+ relevant prior experience
+ restricted tool profile
=
bounded task packet
```

A normal runtime packet should contain:

* one project;
* one stage;
* one task;
* one starting state;
* one permitted tool profile;
* one scope;
* one set of stop conditions;
* one evidence requirement.

Do not put research, design, build, QA, deployment, and handoff into one autonomous mega-prompt.

---

# 12. CONTEXT FAILURE MODES

Document these for future agents:

## Context distraction

Too much irrelevant information distracts the model from the task.

## Context confusion

Background material is mistaken for current instruction.

## Context clash

Multiple sources contain incompatible state.

## Context poisoning

An incorrect assumption is repeatedly carried forward.

## Context drift

Copied prompts diverge from canonical rules.

## Tool overload

The agent receives capabilities unrelated to the current stage.

## Authority inversion

Historical or semantically similar material outranks current verified truth.

The workspace exists partly to prevent these failure modes.

---

# 13. LIVE TARGET-STATE RULE

Mutable operational facts require live verification.

For a Git target verify, where applicable:

```text
repository root
branch
HEAD
approved branch
approved base
remote state
dirty state
worktrees
working-tree ownership
execution hold
approval
```

For infrastructure verify:

```text
hostname
address
service/device
current version
configuration path
service state
backup/checkpoint
rollback readiness
active sessions
execution hold
approval
```

The gate must resolve to:

```text
TARGET GATE: PASS
```

or:

```text
TARGET GATE: FAIL
EXECUTION NOT AUTHORIZED
```

A remembered branch, host, IP, version, or approval is not proof.

---

# 14. SINGLE-WRITER RULE

Only one modifying agent may own a mutable target at a time.

For Git:

one modifying agent per working tree.

Other agents may:

* operate read-only;
* work in separately approved worktrees;
* work on isolated branches;
* review evidence.

The same principle applies to infrastructure configuration and other mutable shared targets.

---

# 15. DURABLE KNOWLEDGE FORMAT

Create a reusable knowledge template.

Recommended frontmatter:

```yaml
---
id: ""
type: concept
title: ""
description: ""
status: draft
authority: supporting
canonical: false
sensitivity: internal

project: ""
domain: ""
tags: []

source:
  type: ""
  path: ""
  commit: ""
  run_id: ""

created_at: ""
updated_at: ""
last_verified: ""
review_by: ""

relationships: []
---
```

Allowed authority values should include:

```text
canonical
current-profile
approved
supporting
historical
candidate
transient
```

---

# 16. CONTRADICTION AND SUPERSESSION RELATIONSHIPS

Do not rely only on deleting or overwriting old knowledge.

Preserve history.

Support relationships such as:

```yaml
relationships:
  - type: supersedes
    target: previous-record-id

  - type: superseded-by
    target: newer-record-id

  - type: contradicts
    target: other-record-id

  - type: contradicted-by
    target: newer-record-id

  - type: supports
    target: related-record-id

  - type: derived-from
    target: source-record-id
```

Example old record:

```yaml
status: superseded
authority: historical
canonical: false

superseded_by:
  - new-record-id

relationships:
  - type: contradicted-by
    target: new-record-id
```

Old information may remain retrievable, but retrieval must understand that it is historical.

---

# 17. EPISODIC RECORD FORMAT

Create a template for significant experiences.

It should capture:

```text
what happened
when
project
stage
target
trigger
observed state
actions taken
outcome
validation
failure
rollback
lesson
source evidence
whether the lesson is reusable
```

Do not store routine conversational chatter as durable episodic memory.

Store high-signal events.

---

# 18. RUNTIME CHECKPOINT FORMAT

Create:

```text
runs/<run-id>/run-state.yaml
```

Template:

```yaml
run_id: ""
project: ""
target_system: ""
workflow: ""
thread_id: ""

status: pending

current_stage: ""
current_step: ""

completed_steps: []
pending_steps: []

approval_required: false
approval_status: not-required
approved_by: ""

model: ""

started_at: ""
updated_at: ""

input_hashes: {}
output_hashes: {}

rollback_reference: ""

resume_instruction: ""
```

Checkpoint after meaningful steps.

A checkpoint records state.

It does not grant permission.

---

# 19. CONTEXT MANIFEST FORMAT

Each controlled run should generate:

```text
context-manifest.yaml
```

Include:

```yaml
run_id: ""
generated_at: ""

project: ""
stage: ""
task: ""

included_sources: []

failure_patterns: []

tool_profile: []

excluded_context:
  - superseded-plans
  - unrelated-history
  - raw-conversation
  - irrelevant-tools

live_target: {}

retrieval: {}

gates: {}
```

For every source include:

```text
path
hash
authority
status
reason-for-inclusion
```

---

# 20. TASK PACKET FORMAT

Create a bounded task-packet template.

It should contain:

```markdown
# Task

# Stage

# Current Verified State

# Read

# Relevant Prior Experience

# Approved Scope

# Permitted Tools

# Prohibited Actions

# Stop Conditions

# Acceptance Criteria

# Required Evidence

# Final Report
```

The `Relevant Prior Experience` section must state:

> Historical hints only. Current verified target state controls execution.

---

# 21. RECALL AND EXPERIENCE LAYER

Create the architecture for a DERIVED recall sidecar.

It must not replace canonical memory.

Default runtime location:

```text
.runtime/recall/
```

This location should normally be excluded from Git.

The recall system must be rebuildable from project files.

Its purpose is:

> Help agents FIND potentially relevant prior knowledge and experience when they do not know where it lives.

Its purpose is NOT:

> Decide what is currently true.

---

# 22. RETRIEVAL IMPLEMENTATION ORDER

Design retrieval in this order:

## Tier 1

Deterministic routing.

Use known paths and current profile.

## Tier 2

Exact search.

Use filenames, identifiers, metadata, dates, commit hashes, model names, version numbers.

## Tier 3

Full-text search.

Use keyword/BM25-style search.

## Tier 4

Metadata and relationship filtering.

Use:

```text
project
stage
authority
status
sensitivity
freshness
relationship
canonical state
```

## Tier 5

Recency.

Recent relevant episodes may receive a ranking benefit, but recency does not override authority.

## Tier 6

Semantic embedding search.

Use only after the earlier mechanisms are available.

## Tier 7

Optional graph/relationship expansion.

Follow:

```text
supersedes
contradicts
supports
derived-from
related-to
```

The ideal future retrieval is hybrid:

```text
current profile
+ exact
+ full text
+ metadata
+ recency
+ semantic
+ relationships
```

---

# 23. VECTOR DATABASE RULE

Do not automatically install a dedicated vector database.

A vector store is:

```text
DERIVED
DISPOSABLE
REBUILDABLE
NON-AUTHORITATIVE
```

Begin with the simplest suitable local mechanism.

A local full-text/metadata index is sufficient for initial operation.

Only add semantic embeddings when benchmarks demonstrate value.

Only add a dedicated vector database when:

* the corpus warrants it;
* multiple consumers need it;
* metadata filtering is understood;
* sensitivity policy is defined;
* rebuild behaviour is defined;
* retrieval evaluation demonstrates an actual benefit.

---

# 24. SESSION-START / CONTROLLED-RUN EPISODIC RECALL

Design future controlled runs to query prior experience BEFORE compiling the final task packet.

Conceptual sequence:

```text
new controlled run
       ↓
read current profile
       ↓
verify live state
       ↓
query relevant historical experience
       ↓
authority and freshness check
       ↓
suppress stale/conflicting candidates
       ↓
compile bounded context
```

Example output:

```markdown
## Relevant Prior Experience

- A previous project encountered a large dirty working tree during takeover.
  Treat unexpected changes as preserved work and perform read-only recon.

- A previous agent followed an obsolete branch from an old handoff.
  Verify repository root, branch, HEAD, remote state and approved base live.

Historical context only. Current verified state controls execution.
```

---

# 25. RETRIEVAL AUTHORITY VERIFICATION

Before a recalled memory enters a task packet:

1. Determine its authority.
2. Determine status.
3. Check supersession.
4. Check contradiction relationships.
5. Check sensitivity.
6. Check project relevance.
7. Check freshness.
8. Determine whether the item is:

   * current fact;
   * approved procedure;
   * historical experience;
   * candidate inference.

Mutable facts must be verified live.

A semantic similarity score is never sufficient proof.

---

# 26. RETRIEVAL FEEDBACK

Create a retrieval-feedback schema.

For each retrieved memory record track:

```yaml
run_id: ""
query_id: ""
record_id: ""

retrieved: true
included_in_packet: false
used_by_agent: false
ignored: false
corrected: false
caused_requery: false
authority_conflict: false

reason: []
```

Possible reasons:

```text
relevant
irrelevant
duplicate
stale
superseded
contradicted
too-low-authority
sensitivity-blocked
useful-historical-example
current-authoritative-source
```

Do not automatically retune retrieval weights initially.

Collect evidence first.

---

# 27. CANDIDATE MEMORY CONSOLIDATION

Create a controlled background-consolidation workflow.

Purpose:

Detect repeated lessons or related episodes.

Example:

```text
seven separate dirty-repository incidents
        ↓
candidate concept
        ↓
"Dirty Repository Takeover"
```

But consolidation must follow:

```text
DETECT
  ↓
PROPOSE
  ↓
HUMAN REVIEW
  ↓
PROMOTE
```

Never:

```text
DETECT
  ↓
AUTOMATICALLY BECOME CANONICAL
```

Candidate records must use:

```yaml
status: candidate
authority: candidate
canonical: false
```

---

# 28. MEMORY PROMOTION POLICY

Create an explicit table.

| Memory                  | Default Location                   | Automatic Write |                   Human Review |
| ----------------------- | ---------------------------------- | --------------: | -----------------------------: |
| runtime state           | `runs/<run-id>/`                   |             yes |                             no |
| raw evidence            | current run                        |             yes |                             no |
| episodic event          | episodes                           |   draft allowed |       before durable promotion |
| current project status  | `PROJECT_STATUS.md`                |         limited | consequential changes reviewed |
| semantic knowledge      | OKF                                |        proposal |                            yes |
| procedural rule         | playbook/canonical file            |   proposal only |                            yes |
| consolidation candidate | retrieval/consolidation/candidates |             yes |           yes before promotion |
| secret                  | external secrets system            |           never |                     prohibited |

---

# 29. SENSITIVITY AND SECRET RULES

Never store secrets in:

* Markdown;
* YAML knowledge files;
* task packets;
* vector stores;
* embedding payloads;
* retrieval logs;
* agent prompts.

Support sensitivity metadata such as:

```text
public
internal
confidential
restricted
secret-reference-only
```

A retrieval index must respect the same sensitivity policy as the source material.

---

# 30. FAILURE-PATTERN LIBRARY

Populate initial cards explaining these failures.

## stale-branch-or-dead-base

Historical branch information was mistaken for current truth.

Required behaviour:

verify branch and base live.

## dirty-tree-collision

Unexpected uncommitted work was altered or absorbed.

Required behaviour:

preserve and recon.

## wrong-target

Agent operated on the wrong repository, host, file tree, or service.

Required behaviour:

verify target identity.

## execution-hold-violation

Agent acted despite explicit user hold.

Required behaviour:

stop execution.

## stale-handoff-conflict

Old handoff conflicts with current state.

Required behaviour:

apply authority hierarchy.

## multiple-agents-one-working-tree

Two modifying agents collide.

Required behaviour:

single writer or isolated worktree.

## scope-expansion

Agent turns a narrow task into broad refactor.

Required behaviour:

stay bounded.

## false-completion-claim

Agent claims success without evidence.

Required behaviour:

completion requires validation.

## live-state-not-verified

Agent relied on memory instead of current evidence.

Required behaviour:

gather live state.

---

# 31. TOOL PROFILES

Create stage-specific tool profiles.

## Triage

Read and classify only.

## Intake

Read sources and write brief.

## Research

Read, search, inspect, and write evidence.

## Design

Read approved inputs and write design.

## Build

Scoped editing plus explicitly approved validation.

Do not automatically allow:

```text
merge
push
deploy
reset
clean
restore
stash
rebase
broad dependency change
```

## QA

Inspect and validate.

Do not silently repair unless permitted.

## Handoff

Update status and records.

Do not introduce implementation.

---

# 32. MODEL NEUTRALITY

The workspace must not depend on a single vendor or model.

Model-specific instruction files may exist only as thin adapters.

They may explain:

* how that model discovers `AGENTS.md`;
* how to invoke tools;
* model-specific syntax.

They must not become independent sources of project truth.

Do not duplicate canonical rules into many model-specific files unless unavoidable.

---

# 33. LOCAL AND SMALL MODEL GOVERNANCE

Smaller or local models may perform:

* inventory;
* recon;
* search;
* classification;
* summarisation;
* bounded drafting;
* routine worker tasks.

They must not independently approve:

* destructive changes;
* security decisions;
* architecture;
* production deployment;
* release;
* privacy-sensitive actions;
* execution-hold exceptions;
* high-consequence target changes.

Escalate these decisions.

---

# 34. RETRIEVAL EVALUATION AS A FIRST-CLASS SUBSYSTEM

Create:

```text
retrieval/evaluation/
```

with a starter golden set.

Test at least these categories.

## Current Truth Tests

Examples:

```text
What branch is currently approved?
Is build currently authorised?
What is the next safe action?
```

Historical records should not override current profile/live state.

## Historical Experience Tests

Examples:

```text
What happened previously when a repository was very dirty?
What previous failure involved an obsolete branch?
```

Relevant episodic records SHOULD be retrieved.

## Procedural Tests

Examples:

```text
What rules apply before modifying production?
What happens during an execution hold?
```

Canonical procedure should win.

## Supersession Tests

Create deliberately conflicting old and new records.

Verify that the current record wins.

## Sensitivity Tests

Ensure inaccessible records are not surfaced.

---

# 35. RETRIEVAL METRICS

Document and prepare to measure:

```text
Recall@K
Precision@K
authority correctness
freshness correctness
supersession correctness
provenance correctness
sensitivity compliance
stale leakage
false positives
latency
token cost
```

Also create:

```text
DANGEROUS AUTHORITY ERROR RATE
```

Definition:

A historical, supporting, candidate, or semantic memory causes the system to give an incorrect CURRENT operational instruction.

Target:

```text
approximately zero
```

This metric is more important than maximum semantic recall.

---

# 36. HANDOFF

Create:

```text
stages/06-handoff/output/current-handoff.md
```

It must contain:

```text
current stage
current target
branch / HEAD / system version where applicable
dirty/live state
active hold
approved actions
prohibited actions
latest completed run
latest commit
key decisions
known issues
next safe action
files next agent should read
```

The handoff is a convenience summary.

It remains below current live state and `PROJECT_STATUS.md` in authority.

---

# 37. GIT AND CHANGE CONTROL

If this workspace is in Git:

Before modifying:

```text
git status
git branch
git rev-parse HEAD
```

Preserve existing work.

For a fresh workspace:

* stage only created workspace files;
* do not stage unrelated files;
* use a clear commit message;
* do not push unless explicitly authorised.

Suggested initial commit:

```text
Create model-neutral persistent project memory workspace
```

---

# 38. TRANSIENT VERSUS DURABLE

Transient:

```text
runs/
raw logs
temporary research
draft outputs
tool transcripts
scratch files
```

Durable:

```text
PROJECT_STATUS.md
approved OKF knowledge
approved decisions
approved playbooks
approved handoff
canonical instructions
```

Do not automatically promote transient content.

Promotion must be deliberate.

---

# 39. BACKGROUND MEMORY CURATION

A future background process may:

* inspect completed run evidence;
* identify recurring concepts;
* identify stale records;
* identify contradictions;
* create candidate episodic summaries;
* propose semantic knowledge;
* suggest relationship edges.

It must NOT:

* silently rewrite canonical instructions;
* silently change project status;
* silently approve deployment;
* silently convert candidate knowledge to canonical knowledge.

All consequential promotions remain reviewable and reversible.

---

# 40. INITIAL FILE POPULATION

Do not create empty placeholder files where meaningful starter content can safely be written.

Populate:

* `AGENTS.md`;
* root `CONTEXT.md`;
* `PROJECT_STATUS.md`;
* manifest;
* memory policy;
* authority policy;
* retrieval policy;
* tool profiles;
* all stage contracts;
* all templates;
* OKF indexes;
* initial failure cards;
* recall system README;
* evaluation README;
* starter golden-set examples;
* handoff template;
* run-state template;
* context-manifest template;
* retrieval-feedback template.

Use unresolved markers instead of fabricated project facts.

---

# 41. INITIAL RECALL BACKEND

Do not deploy a complex vector database as part of the bootstrap unless explicitly requested.

The initial recall architecture should support:

```text
filesystem routing
+ exact search
+ metadata search
+ full-text search
+ recency
+ relationship awareness
```

Semantic embeddings should be treated as an optional next stage.

Document the interface required for future semantic retrieval.

---

# 42. BACKEND-NEUTRAL RECALL INTERFACE

Document generic operations conceptually equivalent to:

```text
Index-Knowledge
Recall-Experience
Search-Knowledge
Verify-MemoryAuthority
Record-RetrievalFeedback
Propose-MemoryConsolidation
Rebuild-MemoryIndex
Test-MemoryRetrieval
```

Do not lock the project to:

* Qdrant;
* SQLite;
* PostgreSQL;
* IAI-PME;
* LangChain;
* LangGraph;
* Ollama;
* any single embedding model.

Those are replaceable implementations.

---

# 43. BOOTSTRAP VALIDATION

After creation, validate:

## Structural

* all required directories exist;
* all canonical root files exist;
* all seven stages exist;
* all stage contracts exist;
* runtime templates exist;
* recall/evaluation structure exists.

## Instruction

* no conflicting canonical instructions;
* authority hierarchy is documented;
* current profile is distinguished from history;
* recall is explicitly non-authoritative;
* execution holds are explicit;
* destructive actions require approval.

## Memory

* durable knowledge uses metadata;
* episodic and semantic memory are separated;
* runtime state is separate;
* supersession relationships are supported;
* memory promotion rules exist.

## Retrieval

* retrieval policy exists;
* current truth and historical recall are distinguished;
* vector stores are derived;
* feedback schema exists;
* evaluation framework exists.

## Security

* no secrets were written;
* `.runtime/` is ignored where appropriate;
* sensitive data rules exist.

## Model neutrality

Search for vendor-specific doctrine.

Vendor-specific content is permitted only in adapters.

---

# 44. BOOTSTRAP REPORT

Create:

```text
setup/bootstrap-report.md
```

Include:

```text
project name
project root
mode confirmed
date
structure created
files created
files skipped
specification version
unresolved facts
initial status
active holds
retrieval backend status
semantic retrieval status
Git status
commit if any
validation result
recommended first controlled run
```

---

# 45. INITIAL PROJECT STATUS

After bootstrap, default to:

```text
current stage: 00-triage or 01-intake
execution hold: active
build approved: false
QA approved: false
deployment approved: false
```

Do not remove the hold merely because the workspace now exists.

The bootstrap establishes governance.

It does not approve project implementation.

---

# 46. FINAL OUTPUT TO THE USER

Return a concise but complete report containing:

1. Fresh-project mode confirmation.
2. Project root.
3. Complete top-level tree.
4. Number of files/directories created.
5. Canonical files created.
6. Memory layers created.
7. Retrieval/recall components created.
8. Evaluation components created.
9. Active holds.
10. Unresolved variables.
11. Validation results.
12. Git branch/status.
13. Commit hash if created.
14. Any deviations from this specification.
15. Exact next safe action.
16. Suggested first controlled-run command or instruction.

Do not simply say "complete".

Provide evidence.

---

# 47. NON-GOALS

Do NOT attempt during bootstrap to:

* build the application;
* refactor target code;
* deploy;
* install a vector database;
* import every previous conversation;
* capture every transcript as durable memory;
* automatically generate canonical knowledge from historical logs;
* remove old project work;
* decide architecture unrelated to the memory system;
* grant yourself future approval.

---

# 48. ACCEPTANCE CRITERIA

The bootstrap succeeds only if:

* the project can be understood from the filesystem alone;
* a new model can determine where to start;
* current truth is separate from history;
* history remains available;
* runtime state can be resumed;
* old knowledge can be marked superseded rather than erased;
* relevant prior experience can later be retrieved;
* recall cannot override authority;
* semantic/vector search remains optional and derived;
* retrieval usefulness can be measured;
* candidate consolidation requires review;
* secrets are excluded;
* future agents receive bounded stage-specific context;
* consequential work remains controlled by explicit gates;
* the entire retrieval index can be destroyed and rebuilt without losing canonical project truth.

The final architecture must embody:

> Recall may suggest. Authority decides. Live state verifies.

```

### One refinement I would make in practice

I would now treat this as the **canonical fresh-project bootstrap specification**, not something we paste into every subsequent agent session. Once the agent creates the workspace, routine work should use the much smaller `AGENTS.md + PROJECT_STATUS.md + stage CONTEXT.md + compiled task packet` path.

That distinction is important: this prompt teaches the **first agent how to build the memory/control system**; it is deliberately detailed. Future worker agents should never need all of it in their context. 
```
