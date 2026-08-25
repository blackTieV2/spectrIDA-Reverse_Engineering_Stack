# model-adapters/

Thin, model-specific adapters ONLY: how a given model/agent discovers
`AGENTS.md`, invokes tools, and any syntax quirks.

Rules:

- Adapters never contain project truth — link to canonical files instead.
- No vendor doctrine outside this directory.
- If you find yourself duplicating a canonical rule here, stop: fix the
  canonical file and reference it.
