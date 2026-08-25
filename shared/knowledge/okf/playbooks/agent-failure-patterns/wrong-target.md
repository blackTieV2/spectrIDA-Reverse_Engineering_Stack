---
id: "fp-wrong-target"
type: playbook
title: "wrong-target"
status: approved
authority: approved
project: "spectrida-re-stack"
tags: [failure-pattern]
---

# wrong-target

**What happens:** Agent operated on the wrong repository, host, file tree, or service.

**Required behaviour:** Verify target identity before acting: repo root, remote URL, hostname. For this project: fork = blackTieV2/..., upstream = ggfuchsi-oss/... — never confuse them.

**If you notice it happening:** stop, record an episodic record
(`shared/templates/episodic-record.template.md`), and surface it to the user.
