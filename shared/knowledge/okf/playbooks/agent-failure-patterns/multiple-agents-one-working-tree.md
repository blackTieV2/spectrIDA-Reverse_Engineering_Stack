---
id: "fp-multiple-agents-one-working-tree"
type: playbook
title: "multiple-agents-one-working-tree"
status: approved
authority: approved
project: "spectrida-re-stack"
tags: [failure-pattern]
---

# multiple-agents-one-working-tree

**What happens:** Two modifying agents collide on one working tree.

**Required behaviour:** Single writer per working tree. Others go read-only or to an isolated worktree/branch.

**If you notice it happening:** stop, record an episodic record
(`shared/templates/episodic-record.template.md`), and surface it to the user.
