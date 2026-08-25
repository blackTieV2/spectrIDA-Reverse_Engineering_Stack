# retrieval/ — the DERIVED recall sidecar

Helps agents FIND potentially relevant prior knowledge. Never decides what
is currently true. Policy: `_config/retrieval-policy.yaml`.

- Runtime index lives in `.runtime/recall/` (gitignored, rebuildable).
- `schemas/` — record/relationship/retrieval-event shapes.
- `evaluation/` — golden set + scoring; Dangerous Authority Error Rate ≈ 0
  is the metric that matters.
- `consolidation/candidates/` — DETECT→PROPOSE output awaiting human review.

Initial backend: filesystem routing + exact + full-text + metadata +
relationship awareness. No vector DB unless benchmarks justify one.
