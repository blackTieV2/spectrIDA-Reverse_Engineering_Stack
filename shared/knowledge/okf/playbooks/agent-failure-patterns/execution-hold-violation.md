---
id: "fp-execution-hold-violation"
type: playbook
title: "execution-hold-violation"
status: approved
authority: approved
project: "spectrida-re-stack"
tags: [failure-pattern]
---

# execution-hold-violation

**What happens:** Agent acted despite an explicit hold.

**Required behaviour:** Stop execution. While `execution_hold: true`, only read-only recon and drafting are permitted.

**If you notice it happening:** stop, record an episodic record
(`shared/templates/episodic-record.template.md`), and surface it to the user.
