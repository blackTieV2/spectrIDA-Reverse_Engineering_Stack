#!/usr/bin/env python3
"""rebuild_recall_index — workspace utility (STUB).

Interface
---------
python rebuild_recall_index.py

Intended behaviour
------------------
Rebuild .runtime/recall/ from the filesystem (OKF + status + stage contracts + run packets). The index is derived/disposable — deleting it must never lose canonical truth.

Status: documented stub. Implement when the workspace workflow needs it.
Deviations from spec v1.0: implemented as Python for cross-platform use
(the operator's machine is Windows; .ps1 wrappers may be added later).
"""
import sys

if __name__ == "__main__":
    sys.exit("rebuild_recall_index: stub — see module docstring for the intended interface.")
