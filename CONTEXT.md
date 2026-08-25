# CONTEXT.md — Stage Router

Routing only. No project knowledge lives here.

| If the task is…                                          | Stage          |
|----------------------------------------------------------|----------------|
| "Look at this", triage a request, classify risk          | `00-triage`    |
| Define goal, constraints, success criteria, stakeholders | `01-intake`    |
| Gather evidence, read-only recon, validate assumptions   | `02-research`  |
| Turn approved requirements into an implementation design | `03-design`    |
| Implement the approved design (needs gates + approval)   | `04-build`     |
| Validate a deliverable against acceptance criteria       | `05-qa`        |
| Consolidate state, evidence, next safe action            | `06-handoff`   |

Rules:

- One run = one stage. Read the stage's `CONTEXT.md` before acting.
- Stage `output/` holds deliverables of that stage only.
- The current stage is recorded in `PROJECT_STATUS.md` — trust that file,
  not your memory of a previous session.
