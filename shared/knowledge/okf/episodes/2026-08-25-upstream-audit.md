---
id: "ep-2026-08-25-001"
type: episode
title: "Independent audit of upstream spectrIDA"
status: approved
authority: historical
project: "spectrida-re-stack"
stage: "02-research"
occurred_at: "2026-08-25"
tags: [audit, packaging, x86]
relationships: []
---

# Independent audit of upstream spectrIDA (c1c0570)

- **Trigger:** evaluate README claims before adopting the tool.
- **Observed state:** core claims real (sharded idalib pipeline, format
  plugins, Ollama naming, Neo4j+MCP, phantomrt); packaging broken on clean
  install; x86-32 misdecoded; Windows-hardcoded paths; node_modules
  committed; README says "names from pseudocode" but the model is fed
  disassembly + call-chain context; 229 pre-existing ruff errors in
  `verify/`+`memory/`; upstream history squashed to a single commit.
- **Actions taken:** full source read; dependency simulation (no-torch,
  no-lz4); test suite runs (30 passed once lz4 installed).
- **Outcome:** fork adopted with hardening fixes (see dec-2026-08-25-001).
- **Lesson:** READMEs are marketing until the code says otherwise — even
  honest, self-deprecating ones. Verify install paths on a CLEAN venv.
- **Reusable?** yes.
