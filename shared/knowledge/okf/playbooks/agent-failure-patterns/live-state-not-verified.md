---
id: "fp-live-state-not-verified"
type: playbook
title: "live-state-not-verified"
status: approved
authority: approved
project: "spectrida-re-stack"
tags: [failure-pattern]
---

# live-state-not-verified

**What happens:** The agent relied on memory instead of current evidence.

**Required behaviour:** Gather live state. A remembered branch, version, path, or approval is not proof.

**If you notice it happening:** stop, record an episodic record
(`shared/templates/episodic-record.template.md`), and surface it to the user.
