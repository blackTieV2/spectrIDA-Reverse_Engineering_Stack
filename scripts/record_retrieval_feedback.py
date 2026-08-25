#!/usr/bin/env python3
"""record_retrieval_feedback — workspace utility (STUB).

Interface
---------
python record_retrieval_feedback.py --run <run-id> --record <id> --reason relevant

Intended behaviour
------------------
Append a retrieval-feedback.yaml entry to the run. Collect evidence; do not retune weights.

Status: documented stub. Implement when the workspace workflow needs it.
Deviations from spec v1.0: implemented as Python for cross-platform use
(the operator's machine is Windows; .ps1 wrappers may be added later).
"""
import sys

if __name__ == "__main__":
    sys.exit("record_retrieval_feedback: stub — see module docstring for the intended interface.")
