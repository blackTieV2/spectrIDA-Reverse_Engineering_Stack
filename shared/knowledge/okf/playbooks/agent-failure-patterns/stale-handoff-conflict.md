---
id: "fp-stale-handoff-conflict"
type: playbook
title: "stale-handoff-conflict"
status: approved
authority: approved
project: "spectrida-re-stack"
tags: [failure-pattern]
---

# stale-handoff-conflict

**What happens:** An old handoff conflicts with current state.

**Required behaviour:** Apply the authority hierarchy: live state > PROJECT_STATUS.md > handoff. Record the conflict; do not silently reconcile.

**If you notice it happening:** stop, record an episodic record
(`shared/templates/episodic-record.template.md`), and surface it to the user.
