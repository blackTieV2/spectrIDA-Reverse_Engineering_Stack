---
id: "fp-dirty-tree-collision"
type: playbook
title: "dirty-tree-collision"
status: approved
authority: approved
project: "spectrida-re-stack"
tags: [failure-pattern]
---

# dirty-tree-collision

**What happens:** Unexpected uncommitted work was altered or absorbed.

**Required behaviour:** Preserve and recon. A dirty tree you didn't create is someone else's work in progress — read-only until the user clarifies ownership.

**If you notice it happening:** stop, record an episodic record
(`shared/templates/episodic-record.template.md`), and surface it to the user.
