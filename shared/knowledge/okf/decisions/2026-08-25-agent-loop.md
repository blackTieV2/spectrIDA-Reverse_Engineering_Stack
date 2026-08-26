---
id: dec-2026-08-25-002
title: Build chain decisions and agent-loop (tp-004) approach
date: 2026-08-25
status: approved
decider: human (Authority) via "do it ensure all decisions are documentd"
related_packets:
  - 2026-08-25-explain-mode-design.md        # tp-001 — built, pushed
  - 2026-08-25-dynamic-feedback-design.md    # tp-002 → 002a — built, pushed
  - 2026-08-25-patching-and-backend-design.md # tp-003 — built, push pending
  - 2026-08-25-agent-loop-design.md          # tp-004 — this build
---

# Decision chain — full feature program (Ghidra/sidebar evaluation → 4 packets)

## Context

The sidebar evaluation produced four feature candidates, ranked by
value-to-spectrIDA cost. The user chose "design all four as task packets,
then build one step at a time." This record pins the decisions made along
the way so the project goal and status are never ambiguous.

## Decisions

1. **Build order: 001 → 002 → 003 → 004.** Chosen by dependency, not
   excitement: explain mode (001) is the prompt contract the agent loop
   (004) reuses; dynamic feedback (002) is the provenance pattern 004's
   memory records follow; patching (003) is independent but its journal
   discipline informs 004's audit trail. *Status: held — 001, 002a, 003
   built in that order.*

2. **tp-002 revised to 002a after live-state falsification.** The packet
   claimed graph annotation was a missing seam; pre-build verification
   found `hunt_crashes`/`live_trace` already annotate (`dyn_*` SET-only)
   and `dynamic_overview` already reads. Stop condition fired; scope cut
   to provenance fields + OKF crash cards + TUI markers. *Lesson: grep
   call sites before claiming a gap.* Recorded in ep-2026-08-25-004.

3. **Free backend port: NO-GO today (tp-003 Part B).** Capability matrix
   and cost analysis in stages/02-research/output/backend-portability-report.md.
   The facade is type-clean, but the idalib-native shard MERGE_LOADER is
   the real port cost. Recommendation D now (protocol extraction rides
   with tp-004), B later (Ghidra only if free users appear), C never
   (r2pipe cannot own the db role).

4. **Agent loop calls MCP functions in-process, not over the wire.**
   The loop imports the same async callables the MCP tools wrap. No
   socket, no auth, no stdio dance inside one process. If a remote agent
   is ever wanted, the same tools are already exposed over MCP — the
   loop gains nothing by talking to itself through a socket.

5. **verify_decompilation is a STUB — medium-confidence gate degrades
   gracefully.** Live-state check during 004 build found the tool
   returns `{"status": "ready_for_verification"}` only (full pipeline
   needs binary-bytes extraction). Decision: the planner still routes
   medium-confidence names through the *intent* to verify, but when the
   response carries the stub marker the item falls through to the human
   queue with `reason: "verify_decompilation stub"`. Auto-apply remains
   restricted to high confidence. When the real verifier lands, no loop
   change is needed — the gate already keys off the response shape.

6. **Budgets are hard caps, convergence is the stop signal.**
   200 LLM calls / 30 min / 100 renames per run; convergence = coverage
   delta < 2% over 3 iterations. Budget exhaustion is a normal exit,
   not an error — the run report says which cap fired.

7. **OKF memory is draft-only, single-writer.** The loop may write
   draft records to `shared/knowledge/okf/`; it never approves its own
   records and never writes outside the OKF tree. Matches workspace
   doctrine: agent-authored records are drafts until human-approved.

## Consequences

- The fork now has: explain mode (E key), dynamic markers (✖▶?) with
  provenance, draft crash cards, verified patching with journal and
  auto-revert, and (this build) a bounded agent loop.
- Nothing in the loop depends on a live Ollama at test time — all LLM
  behavior is scripted via dependency injection.
- Protocol extraction (option D) is deliberately NOT in this build;
  it is a follow-up once the loop's real call pattern is observed.

## Status of the program after this build

| Packet | Scope | Built | Pushed |
|--------|-------|-------|--------|
| tp-001 | Explain mode | ✅ | ✅ |
| tp-002a | Dynamic feedback (reduced) | ✅ | ✅ |
| tp-003 | Patching + backend NO-GO | ✅ | ⏳ pending device auth |
| tp-004 | Agent loop | ✅ this build | ⏳ with 003 |

Feature program complete after tp-004. Remaining work is live
acceptance on the user's machine, then protocol extraction as a
follow-up packet if the loop's call pattern justifies it.
