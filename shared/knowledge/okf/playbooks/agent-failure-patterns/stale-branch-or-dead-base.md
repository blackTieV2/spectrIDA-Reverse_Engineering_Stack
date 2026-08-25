---
id: "fp-stale-branch-or-dead-base"
type: playbook
title: "stale-branch-or-dead-base"
status: approved
authority: approved
project: "spectrida-re-stack"
tags: [failure-pattern]
---

# stale-branch-or-dead-base

**What happens:** Historical branch information was mistaken for current truth.

**Required behaviour:** Verify branch and base live: `git branch --show-current`, `git rev-parse HEAD`, `git fetch` + compare remote, before any change.

**If you notice it happening:** stop, record an episodic record
(`shared/templates/episodic-record.template.md`), and surface it to the user.
