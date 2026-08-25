# scripts/

Pipeline scripts (`populate_graph.py`, `upload_gguf.py`), dev one-shots
(`dev/`), and workspace utilities (below, currently documented stubs):

- `new_controlled_run.py` — mint a `runs/<run-id>/` from `_template/`
- `compile_agent_context.py` — build a bounded task packet from canonical sources
- `verify_target_state.py` — live-state check; prints TARGET GATE: PASS/FAIL
- `rebuild_recall_index.py` — rebuild `.runtime/recall/` from workspace files
- `search_recall_memory.py` — query the recall index (tiers 1-4)
- `verify_recall_authority.py` — pre-packet authority/freshness checks
- `record_retrieval_feedback.py` — append a retrieval-feedback record
- `propose_memory_consolidation.py` — DETECT→PROPOSE into `retrieval/consolidation/candidates/`
- `test_recall_system.py` — run the golden set, report metrics
