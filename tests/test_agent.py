"""Tests for the bounded agent loop — scripted fake LLM, no Ollama/IDA/Neo4j."""
from __future__ import annotations

import asyncio

import pytest

from spectrida.agent import (Action, AgentLoop, Budget, BudgetExhausted,
                             BudgetTracker, Planner)
from spectrida.agent.memory import write_naming_pattern
from spectrida.core.explain import Explanation


def run(coro):
    return asyncio.run(coro)


def expl(name: str, conf: str = "high", purpose: str = "does a thing") -> Explanation:
    return Explanation(purpose=purpose, suggested_name=name, confidence=conf,
                       confidence_why="scripted")


# ── budget ──────────────────────────────────────────────────────────────────

class TestBudget:
    def test_llm_cap_fires(self):
        t = BudgetTracker(Budget(llm_calls=2))
        t.spend_llm(); t.spend_llm()
        with pytest.raises(BudgetExhausted) as e:
            t.spend_llm()
        assert e.value.cap == "llm_calls"

    def test_rename_cap_fires(self):
        t = BudgetTracker(Budget(renames=1))
        t.spend_rename()
        with pytest.raises(BudgetExhausted) as e:
            t.spend_rename()
        assert e.value.cap == "renames"

    def test_time_cap_fires(self):
        clock = FakeClock()
        t = BudgetTracker(Budget(seconds=10), clock=clock)
        clock.advance(11)
        with pytest.raises(BudgetExhausted) as e:
            t.check()
        assert e.value.cap == "seconds"

    def test_summary_counts(self):
        t = BudgetTracker(Budget(llm_calls=10, renames=5))
        t.spend_llm(3); t.spend_rename()
        s = t.summary()
        assert s["llm_calls"] == "3/10" and s["renames"] == "1/5"


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def advance(self, dt: float):
        self.t += dt


# ── planner ─────────────────────────────────────────────────────────────────

class TestPlanner:
    p = Planner()

    def test_high_confidence_auto_applies(self):
        item = self.p.plan(0x1000, "sub_1000", expl("parse_header", "high"))
        assert item.action is Action.AUTO_APPLY
        assert item.suggested_name == "parse_header"

    def test_medium_routes_to_verify(self):
        item = self.p.plan(0x1000, "sub_1000", expl("maybe_checksum", "medium"))
        assert item.action is Action.VERIFY_THEN_QUEUE

    def test_low_goes_to_human_queue(self):
        item = self.p.plan(0x1000, "sub_1000", expl("idk_helper", "low"))
        assert item.action is Action.HUMAN_QUEUE
        assert not item.applied

    def test_unusable_name_skips(self):
        for bad in ("", "sub_1234", "not a name!", "x" * 200):
            item = self.p.plan(0x1000, "sub_1000", expl(bad, "high"))
            assert item.action is Action.SKIP, bad

    def test_unchanged_name_skips(self):
        item = self.p.plan(0x1000, "parse_header", expl("parse_header", "high"))
        assert item.action is Action.SKIP

    def test_failed_explain_skips(self):
        assert self.p.plan(0x1000, "sub_1000", None).action is Action.SKIP

    def test_verify_stub_degrades_to_queue(self):
        item = self.p.plan(0x1000, "sub_1000", expl("maybe_checksum", "medium"))
        item = self.p.handle_verify_result(
            item, {"status": "ready_for_verification",
                   "note": "Full pipeline requires binary bytes extraction"})
        assert item.action is Action.HUMAN_QUEUE
        assert item.verify_note == "verify_decompilation stub"

    def test_real_verifier_would_upgrade(self):
        item = self.p.plan(0x1000, "sub_1000", expl("maybe_checksum", "medium"))
        item = self.p.handle_verify_result(item, {"verified": True})
        assert item.action is Action.AUTO_APPLY


# ── loop (scripted seams) ───────────────────────────────────────────────────

class FakeWorld:
    """In-memory binary: N functions, scripted explanations per address."""

    def __init__(self, n: int, conf_by_addr: dict[int, str] | None = None):
        self.funcs = [{"start": 0x1000 + 0x10 * i, "name": f"sub_{0x1000 + 0x10 * i:x}"}
                      for i in range(n)]
        self.conf_by_addr = conf_by_addr or {}
        self.renamed: dict[int, str] = {}
        self.llm_calls = 0

    async def list_functions(self):
        return list(self.funcs)

    async def baseline(self):
        named = sum(1 for f in self.funcs if not f["name"].startswith("sub_"))
        return {"coverage_pct": round(100 * named / len(self.funcs), 1)}

    async def explain(self, addr: int):
        self.llm_calls += 1
        conf = self.conf_by_addr.get(addr, "high")
        return expl(f"agent_fn_{addr:x}", conf)

    async def rename(self, addr: int, name: str, comment: str):
        self.renamed[addr] = name
        for f in self.funcs:
            if f["start"] == addr:
                f["name"] = name
        return {"renamed": True}

    async def verify(self, addr: int, pseudo: str):
        return {"status": "ready_for_verification"}

    def loop(self, **kw) -> AgentLoop:
        return AgentLoop(binary="fake.exe", list_functions=self.list_functions,
                         baseline=self.baseline, explain=self.explain,
                         rename=self.rename, verify=self.verify, **kw)


class TestLoop:
    def test_high_confidence_names_applied_and_converges(self, tmp_path):
        w = FakeWorld(5)
        result = run(w.loop(okf_root=tmp_path).run())
        rep = result.report
        assert len(w.renamed) == 5
        assert rep.coverage_end == 100.0
        assert rep.stop_reason in ("no unnamed functions remain",
                                   "all remaining functions processed")
        assert rep.to_dict()["status"] == "draft"
        assert result.report_path and result.report_path.exists()

    def test_low_confidence_queued_not_applied(self, tmp_path):
        addrs = {0x1000 + 0x10 * i: "low" for i in range(3)}
        w = FakeWorld(3, conf_by_addr=addrs)
        rep = run(w.loop(okf_root=tmp_path).run()).report
        assert not w.renamed
        assert len(rep.by_action(Action.HUMAN_QUEUE)) == 3

    def test_medium_degrades_via_stub_to_queue(self, tmp_path):
        w = FakeWorld(2, conf_by_addr={0x1000: "medium", 0x1010: "medium"})
        rep = run(w.loop(okf_root=tmp_path).run()).report
        assert not w.renamed
        queue = rep.by_action(Action.HUMAN_QUEUE)
        assert len(queue) == 2
        assert all(i.verify_note == "verify_decompilation stub" for i in queue)

    def test_budget_exhaustion_is_normal_exit(self, tmp_path):
        w = FakeWorld(50)
        rep = run(w.loop(budget=Budget(llm_calls=5), okf_root=tmp_path).run()).report
        assert rep.stop_reason == "budget exhausted: llm_calls"
        assert rep.to_dict()["budget"]["llm_calls"] == "5/5"

    def test_failed_explains_skip_and_terminate(self, tmp_path):
        # All explains fail → everything skipped once, loop exits cleanly.
        w = FakeWorld(4)

        async def boom(addr):
            raise RuntimeError("model down")
        w.explain = boom
        rep = run(w.loop(okf_root=tmp_path).run()).report
        assert rep.stop_reason == "all remaining functions processed"
        assert all(i.action is Action.SKIP for i in rep.items)

    def test_convergence_detector(self):
        # Unit-pin the stop signal itself: flat coverage over the window.
        assert not AgentLoop._converged([10.0])
        assert not AgentLoop._converged([10.0, 14.0, 18.0, 22.0])
        assert AgentLoop._converged([10.0, 11.0, 11.5, 12.0, 12.5])
        assert not AgentLoop._converged([10.0, 11.0, 11.5, 12.0, 15.0])

    def test_max_iterations_cap(self, tmp_path):
        # Progress every iteration (rename one per pass) never converges fast
        # enough — but the iteration cap still terminates the run.
        w = FakeWorld(100)
        rep = run(w.loop(max_iterations=2, okf_root=tmp_path).run()).report
        assert rep.iterations <= 2

    def test_okf_pattern_drafts_written_and_deduped(self, tmp_path):
        w = FakeWorld(3)
        run(w.loop(okf_root=tmp_path).run())
        pats = list((tmp_path / "playbooks" / "naming-patterns").glob("*.md"))
        assert len(pats) == 3
        assert "status: draft" in pats[0].read_text()

    def test_report_marks_human_queue(self, tmp_path):
        w = FakeWorld(2, conf_by_addr={0x1000: "high", 0x1010: "low"})
        rep = run(w.loop(okf_root=tmp_path).run()).report
        md = rep.to_markdown()
        assert "agent_fn_1000" in md and "Human queue" in md
        d = rep.to_dict()
        assert len(d["applied"]) == 1 and len(d["human_queue"]) == 1


# ── memory ──────────────────────────────────────────────────────────────────

class TestMemory:
    def test_dedupes_per_run(self, tmp_path):
        kw = dict(run_id="r1", binary="b.exe", addr=0x1000, name="parse_header",
                  confidence="high", confidence_why="x", purpose="p",
                  date="2026-08-25")
        p1 = write_naming_pattern(tmp_path, **kw)
        p2 = write_naming_pattern(tmp_path, **kw)
        assert p1 == p2 and p1.exists()

    def test_never_raises_on_bad_path(self, tmp_path):
        blocker = tmp_path / "afile"
        blocker.write_text("not a dir")
        assert write_naming_pattern(blocker / "sub", run_id="r", binary="b",
                                    addr=1, name="n", confidence="high",
                                    confidence_why="", purpose="",
                                    date="2026-08-25") is None
