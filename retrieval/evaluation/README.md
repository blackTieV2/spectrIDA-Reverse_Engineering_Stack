# retrieval/evaluation/

Retrieval quality is measured, not assumed.

- `golden-set.yaml` — questions with known-correct expected sources.
- `expected-results.yaml` — which records SHOULD vs MUST NOT surface.
- `scoring.md` — metrics and how to compute them.

Categories covered: current truth, historical experience, procedural,
supersession, sensitivity.

The headline metric is **Dangerous Authority Error Rate ≈ 0** — a stale or
low-authority memory producing a wrong CURRENT instruction. Maximum semantic
recall is secondary.
