"""The bounded agent loop (tp-2026-08-25-004).

One run = iterate over still-unnamed functions, explain each, plan per
confidence thresholds, apply high-confidence names, queue the rest for
a human.  Stops on convergence (coverage delta < 2% over 3 iterations)
or budget exhaustion — whichever comes first.  Every seam is an
injected async callable, so tests script a fake LLM and never touch
Ollama, IDA, or Neo4j.
"""
from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spectrida.agent.budget import Budget, BudgetExhausted, BudgetTracker
from spectrida.agent.memory import write_naming_pattern
from spectrida.agent.planner import Action, PlanItem, Planner
from spectrida.agent.report import RunReport
from spectrida.core.explain import Explanation

CONVERGENCE_DELTA_PCT = 2.0
CONVERGENCE_WINDOW = 3

# Injected seams — same signatures the MCP tools wrap.
ListFns = Callable[[], Awaitable[list[dict]]]
BaselineFn = Callable[[], Awaitable[dict]]
ExplainFn = Callable[[int], Awaitable[Explanation | None]]
RenameFn = Callable[[int, str, str], Awaitable[Any]]
VerifyFn = Callable[[int, str], Awaitable[dict]]


def classify_name(name: str | None) -> str:
    """Three-state classification (tp-2026-09-01-006).

    "unnamed" — sub_* or empty: AI naming work.
    "library" — jump thunks (j_…) or mangled names (MSVC ?, Itanium _ZN):
                known library code resolved by Lumina/symbols. Never
                AI-renamed — the model's job is the user's code, not CRT.
    "named"   — anything else: already meaningful.

    Live falsification 2026-09-01 (BlackTie, Lumina-resolved db): a binary
    with zero sub_* made the old boolean filter report "no unnamed
    functions" — true under its definition, blind to WHY. The loop must
    say which kind of nothing it found.
    """
    if not name or name.startswith("sub_"):
        return "unnamed"
    if name.startswith("j_"):          # jump thunk (incl. j_sub_, j_?…)
        return "library"
    if "?" in name or name.startswith("_ZN"):  # MSVC / Itanium mangling
        return "library"
    return "named"


@dataclass
class LoopResult:
    report: RunReport
    report_path: Path | None


class AgentLoop:
    """Orchestrates one bounded naming run."""

    def __init__(
        self,
        *,
        binary: str,
        list_functions: ListFns,
        baseline: BaselineFn,
        explain: ExplainFn,
        rename: RenameFn,
        verify: VerifyFn,
        budget: Budget | None = None,
        planner: Planner | None = None,
        okf_root: Path | None = None,
        clock=time.monotonic,
        max_iterations: int = 10,
    ) -> None:
        self.binary = binary
        self._list = list_functions
        self._baseline = baseline
        self._explain = explain
        self._rename = rename
        self._verify = verify
        self.tracker = BudgetTracker(budget, clock=clock)
        self.planner = planner or Planner()
        self.okf_root = okf_root
        self.max_iterations = max_iterations
        self.run_id = uuid.uuid4().hex[:8]
        self._seen: set[int] = set()  # processed this run — never re-spend on a queued/skip item

    async def run(self) -> LoopResult:
        report = RunReport(run_id=self.run_id, binary=self.binary,
                           coverage_start=await self._coverage())
        report.coverage_end = report.coverage_start  # honest default: unchanged
        coverage_history = [report.coverage_start]
        stop = "max_iterations reached"
        try:
            for it in range(1, self.max_iterations + 1):
                report.iterations = it
                self.tracker.check()
                all_funcs = await self._list()
                funcs = []
                for f in all_funcs:
                    addr = int(f.get("addr", f.get("start")))
                    if addr in self._seen:
                        continue
                    cls = classify_name(f.get("name"))
                    if cls == "library":
                        report.library_skipped += 1
                        self._seen.add(addr)  # classified once per run
                    elif cls == "unnamed":
                        funcs.append(f)
                if not funcs:
                    suffix = (f" ({report.library_skipped} library/thunk "
                              f"functions skipped)") if report.library_skipped else ""
                    # "no work ever existed" vs "work existed, we finished it" —
                    # library classifications don't count as work
                    stop = (("no unnamed functions remain" if not report.items
                             else "all remaining functions processed") + suffix)
                    break
                for f in funcs:
                    # FunctionInfo uses "start"; graph rows use "addr".
                    addr = int(f.get("addr", f.get("start")))
                    self._seen.add(addr)
                    item = await self._process(addr, f.get("name") or "")
                    report.items.append(item)
                cov = await self._coverage()
                coverage_history.append(cov)
                report.coverage_end = cov
                if self._converged(coverage_history):
                    stop = (f"converged: coverage delta < {CONVERGENCE_DELTA_PCT}% "
                            f"over {CONVERGENCE_WINDOW} iterations")
                    break
        except BudgetExhausted as e:
            stop = f"budget exhausted: {e.cap}"
        report.stop_reason = stop
        report.budget_summary = self.tracker.summary()
        report_path = report.write(self.okf_root / "agent-runs") if self.okf_root else None
        return LoopResult(report=report, report_path=report_path)

    # ── internals ────────────────────────────────────────────────────────────

    async def _process(self, addr: int, current_name: str) -> PlanItem:
        try:
            self.tracker.spend_llm()
        except BudgetExhausted:
            raise
        try:
            expl = await self._explain(addr)
        except Exception:
            expl = None
        item = self.planner.plan(addr, current_name, expl)
        if item.action is Action.VERIFY_THEN_QUEUE:
            try:
                self.tracker.spend_llm()
                vr = await self._verify(addr, "")
            except Exception:
                vr = {}
            item = self.planner.handle_verify_result(item, vr)
        if item.action is Action.AUTO_APPLY:
            self.tracker.spend_rename()
            ok = await self._rename(addr, item.suggested_name,
                                    f"agent: {item.confidence} confidence")
            item.applied = bool(ok if isinstance(ok, bool) else ok.get("renamed", ok))
            if item.applied and self.okf_root:
                write_naming_pattern(
                    self.okf_root, run_id=self.run_id, binary=self.binary,
                    addr=addr, name=item.suggested_name,
                    confidence=item.confidence,
                    confidence_why=item.reason,
                    purpose=expl.purpose if expl else "",
                    date=time.strftime("%Y-%m-%d"),
                )
        return item

    async def _coverage(self) -> float:
        b = await self._baseline()
        return float(b.get("coverage_pct", 0.0))

    @staticmethod
    def _converged(history: list[float]) -> bool:
        if len(history) <= CONVERGENCE_WINDOW:
            return False
        deltas = [abs(history[i] - history[i - 1])
                  for i in range(len(history) - CONVERGENCE_WINDOW, len(history))]
        return all(d < CONVERGENCE_DELTA_PCT for d in deltas)
