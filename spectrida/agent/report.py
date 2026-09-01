"""Run report: what the loop did, why it stopped, what needs a human."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from spectrida.agent.planner import Action, PlanItem


@dataclass
class RunReport:
    run_id: str
    binary: str
    stop_reason: str = "running"
    iterations: int = 0
    coverage_start: float = 0.0
    coverage_end: float = 0.0
    budget_summary: dict = field(default_factory=dict)
    items: list[PlanItem] = field(default_factory=list)
    library_skipped: int = 0  # Lumina/mangled/thunk functions skipped (tp-006)

    def by_action(self, action: Action) -> list[PlanItem]:
        return [i for i in self.items if i.action == action]

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "binary": self.binary,
            "status": "draft",
            "stop_reason": self.stop_reason,
            "iterations": self.iterations,
            "coverage_start": self.coverage_start,
            "coverage_end": self.coverage_end,
            "coverage_delta": round(self.coverage_end - self.coverage_start, 1),
            "budget": self.budget_summary,
            "applied": [vars(i) | {"action": i.action.value}
                        for i in self.items if i.applied],
            "human_queue": [vars(i) | {"action": i.action.value}
                            for i in self.by_action(Action.HUMAN_QUEUE)],
            "skipped": sum(1 for i in self.items if i.action == Action.SKIP),
            "library_skipped": self.library_skipped,
        }

    def to_markdown(self) -> str:
        d = self.to_dict()
        lines = [
            "---",
            f'title: agent run {self.run_id}',
            f'binary: "{self.binary}"',
            "status: draft",
            "author: spectrida-agent",
            "---",
            "",
            f"# Agent run `{self.run_id}` — {self.binary}",
            "",
            f"- **Stop reason:** {self.stop_reason}",
            f"- **Iterations:** {self.iterations}",
            f"- **Coverage:** {self.coverage_start}% → {self.coverage_end}% "
            f"(Δ {d['coverage_delta']}%)",
            f"- **Budget:** {self.budget_summary}",
            f"- **Applied:** {len(d['applied'])} · "
            f"**Human queue:** {len(d['human_queue'])} · "
            f"**Skipped:** {d['skipped']}",
            "",
            "## Human queue (needs review)",
            "",
        ]
        for i in self.by_action(Action.HUMAN_QUEUE):
            lines.append(f"- `0x{i.addr:x}` → suggested `{i.suggested_name}` "
                         f"({i.confidence}: {i.verify_note or i.reason})")
        lines += ["", "## Applied (high confidence)", ""]
        for i in self.items:
            if i.applied:
                lines.append(f"- `0x{i.addr:x}` → `{i.suggested_name}`")
        lines += ["", "*Draft. Approve by flipping `status` after review.*", ""]
        return "\n".join(lines)

    def write(self, out_dir: Path) -> Path | None:
        try:
            d = Path(out_dir)
            d.mkdir(parents=True, exist_ok=True)
            p = d / f"agent-run-{self.run_id}.md"
            p.write_text(self.to_markdown(), encoding="utf-8")
            return p
        except OSError:
            return None
