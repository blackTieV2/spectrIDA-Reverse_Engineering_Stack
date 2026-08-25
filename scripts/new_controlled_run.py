#!/usr/bin/env python3
"""new_controlled_run — workspace utility (STUB).

Interface
---------
python new_controlled_run.py --stage 01-intake --task "<one line>"

Intended behaviour
------------------
Create runs/<run-id>/ from runs/_template/, fill run-state.yaml (status: pending, approval_required per stage), print the run id. Refuses to start if PROJECT_STATUS.md has execution_hold: true and the run's stage is 04-build.

Status: documented stub. Implement when the workspace workflow needs it.
Deviations from spec v1.0: implemented as Python for cross-platform use
(the operator's machine is Windows; .ps1 wrappers may be added later).
"""
import sys

if __name__ == "__main__":
    sys.exit("new_controlled_run: stub — see module docstring for the intended interface.")
