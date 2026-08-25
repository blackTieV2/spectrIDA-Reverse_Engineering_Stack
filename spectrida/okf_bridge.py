"""Bridge: phantomrt crash verdicts -> OKF failure-pattern cards.

When the fuzzer returns ``candidate_crash``, the evidence (reproducing input,
fault address, status counts) is too valuable to live only in a job result
dict. This writes a *draft* knowledge record per (function, run) so the
workspace accumulates crash intelligence. Draft-only per doctrine: a human
promotes records to approved.

Cards land in ``shared/knowledge/okf/playbooks/crash-patterns/`` relative to
the given workspace root. Dedupe key: (addr, run_id) — one card per function
per analysis run, never more.
"""
from __future__ import annotations

import time
from pathlib import Path


def card_dir(okf_root: str | Path) -> Path:
    return Path(okf_root) / "shared/knowledge/okf/playbooks/crash-patterns"


def write_crash_card(
    okf_root: str | Path,
    *,
    binary: str,
    addr: int,
    run_id: str,
    result: dict,
) -> Path | None:
    """Write a draft crash card for a candidate_crash verdict.

    Returns the card path, or None if the verdict is not a crash or a card
    for this (addr, run_id) already exists. Never raises on I/O problems —
    crash cards are best-effort evidence, not a blocking write.
    """
    if result.get("verdict") != "candidate_crash":
        return None

    outdir = card_dir(okf_root)
    path = outdir / f"crash-{addr:x}-{run_id}.md"
    if path.exists():
        return None

    crashes = result.get("crash_inputs", {})
    first_kind, first_input = next(iter(crashes.items()), ("unknown", ""))
    name = result.get("name") or f"sub_{addr:x}"
    today = time.strftime("%Y-%m-%d")

    body = f"""---
id: "crash-{addr:x}-{run_id}"
type: playbook
title: "crash-{name}-{addr:x}"
status: draft
authority: draft
project: "spectrida-re-stack"
tags: [failure-pattern, crash, dynamic-analysis, phantomrt-alpha]
---

# Crash pattern: {name} @ {hex(addr)} ({binary})

**What happens:** Emulation-guided fuzzing produced a `candidate_crash`
verdict — {result.get('unique_crashes', len(crashes))} unique crash site(s)
in {result.get('rounds', '?')} rounds.

**Evidence (phantomrt alpha — treat as lead, not proof):**

- First crash: `{first_kind}`
- Reproducing input (hex): `{first_input[:128]}`
- Reachable blocks seen: {result.get('blocks', '?')}
- Seed source: {result.get('seed_source', 'unknown')} ({result.get('seeds_used', 0)} seeds)
- Status counts: {result.get('status_counts', {})}
- Binary: `{binary}` — run `{run_id}`, recorded {today}

**Required behaviour:** verify manually before trusting — reproduce against
the real target (live_trace or a debugger) before treating as a bug. Alpha
verdicts are leads.

**If you notice it happening:** check whether the crash input exercises the
same parser path as other cards in this folder — clustered fault addresses
usually mean one root cause, not many.
"""
    try:
        outdir.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    except OSError:
        return None
    return path
