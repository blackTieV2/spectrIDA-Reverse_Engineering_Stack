"""Pure decision logic: explanation → action.

Thresholds (per task packet tp-2026-08-25-004):
  high   confidence → auto-apply the suggested name
  medium confidence → intend to verify; if verify_decompilation is still
                      the stub (dec-2026-08-25-002 #5) the item degrades
                      to the human queue instead of being applied
  low / unknown     → human queue, untouched

The planner never performs I/O — it only classifies.  That keeps every
decision unit-testable and the loop's audit trail honest.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from spectrida.core.explain import Explanation

_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")


class Action(str, Enum):
    AUTO_APPLY = "auto_apply"
    VERIFY_THEN_QUEUE = "verify_then_queue"
    HUMAN_QUEUE = "human_queue"
    SKIP = "skip"


@dataclass
class PlanItem:
    """One function's planned disposition."""

    addr: int
    action: Action
    suggested_name: str = ""
    confidence: str = "unknown"
    reason: str = ""
    applied: bool = False
    verify_note: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


def _valid_name(name: str) -> bool:
    return bool(name) and bool(_NAME_RE.match(name)) and not name.startswith("sub_")


class Planner:
    """Classify explanations into actions per confidence thresholds."""

    def plan(self, addr: int, current_name: str, expl: Explanation | None) -> PlanItem:
        if expl is None:
            return PlanItem(addr, Action.SKIP, reason="explain failed")
        name = expl.suggested_name.strip()
        if not _valid_name(name):
            return PlanItem(addr, Action.SKIP, confidence=expl.confidence,
                            reason=f"unusable suggested name: {name!r}")
        if name == current_name:
            return PlanItem(addr, Action.SKIP, suggested_name=name,
                            confidence=expl.confidence, reason="name unchanged")
        conf = expl.confidence.lower()
        if conf == "high":
            return PlanItem(addr, Action.AUTO_APPLY, suggested_name=name,
                            confidence=conf, reason=expl.confidence_why)
        if conf == "medium":
            return PlanItem(addr, Action.VERIFY_THEN_QUEUE, suggested_name=name,
                            confidence=conf, reason=expl.confidence_why)
        return PlanItem(addr, Action.HUMAN_QUEUE, suggested_name=name,
                        confidence=conf, reason=expl.confidence_why)

    def handle_verify_result(self, item: PlanItem, verify_result: dict) -> PlanItem:
        """Fold a verify_decompilation response into the plan item.

        The stub response carries ``status == "ready_for_verification"``;
        per dec-2026-08-25-002 #5 that degrades to the human queue.  A
        future real verifier returning ``verified: true`` would let the
        item upgrade to AUTO_APPLY without any loop change.
        """
        if verify_result.get("verified") is True:
            item.action = Action.AUTO_APPLY
            item.verify_note = "verified"
        elif verify_result.get("status") == "ready_for_verification":
            item.action = Action.HUMAN_QUEUE
            item.verify_note = "verify_decompilation stub"
        else:
            item.action = Action.HUMAN_QUEUE
            item.verify_note = "verification inconclusive"
        return item
