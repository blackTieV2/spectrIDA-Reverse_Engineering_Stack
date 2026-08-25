#!/usr/bin/env python3
"""compile_agent_context — workspace utility (STUB).

Interface
---------
python compile_agent_context.py --run <run-id>

Intended behaviour
------------------
Compile a bounded task packet: AGENTS.md + PROJECT_STATUS.md + stage CONTEXT.md + verified live state + approved scope + relevant references + relevant prior experience (authority-checked) + the stage's tool profile. Writes context-manifest.yaml into the run dir.

Status: documented stub. Implement when the workspace workflow needs it.
Deviations from spec v1.0: implemented as Python for cross-platform use
(the operator's machine is Windows; .ps1 wrappers may be added later).
"""
import sys

if __name__ == "__main__":
    sys.exit("compile_agent_context: stub — see module docstring for the intended interface.")
