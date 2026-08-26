"""Draft-only OKF memory for agent runs.

Writes naming-playbook drafts under
``<okf_root>/playbooks/naming-patterns/``.  Agent-authored records are
drafts until a human approves them (workspace doctrine); the agent is
the single writer for its own files and never writes outside the OKF
tree.  Filesystem failures never abort a run.
"""
from __future__ import annotations

from pathlib import Path

_HEADER = """---
title: agent naming pattern — {name}
date: {date}
status: draft
author: spectrida-agent
source_run: {run_id}
---

# Pattern: `{name}`

- **Confidence:** {confidence} — {confidence_why}
- **First seen at:** 0x{addr:x} in `{binary}`
- **Purpose:** {purpose}

*Draft written by the agent loop. Review, edit, and flip `status` to
`approved` to adopt.*
"""


def write_naming_pattern(
    okf_root: Path,
    *,
    run_id: str,
    binary: str,
    addr: int,
    name: str,
    confidence: str,
    confidence_why: str,
    purpose: str,
    date: str,
) -> Path | None:
    """Write a draft naming-pattern record.  Returns path or None.

    De-dupes per (run, name): a second sighting of the same pattern in
    one run does not rewrite the file.
    """
    try:
        d = Path(okf_root) / "playbooks" / "naming-patterns"
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"pattern-{name}-{run_id}.md"
        if p.exists():
            return p
        p.write_text(_HEADER.format(name=name, date=date, run_id=run_id,
                                    confidence=confidence,
                                    confidence_why=confidence_why or "n/a",
                                    addr=addr, binary=binary,
                                    purpose=purpose or "n/a"),
                     encoding="utf-8")
        return p
    except OSError:
        return None
