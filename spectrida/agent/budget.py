"""Hard budget caps for one agent run.

Exhaustion is a *normal* exit, not an error: the run report records
which cap fired.  Caps are checked before every spend so a run can
never overshoot by more than the operation in flight.
"""
from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Budget:
    """Caps for a single agent run."""

    llm_calls: int = 200
    seconds: float = 30 * 60
    renames: int = 100


class BudgetExhausted(Exception):
    """Raised when a cap fires.  ``cap`` names the exhausted dimension."""

    def __init__(self, cap: str) -> None:
        super().__init__(f"budget exhausted: {cap}")
        self.cap = cap


class BudgetTracker:
    """Mutable spend counter against a frozen :class:`Budget`."""

    def __init__(self, budget: Budget | None = None, *, clock=time.monotonic) -> None:
        self.budget = budget or Budget()
        self.llm_calls = 0
        self.renames = 0
        self._start = clock()
        self._clock = clock

    @property
    def elapsed(self) -> float:
        return self._clock() - self._start

    def check(self) -> None:
        """Raise :class:`BudgetExhausted` if any cap has fired."""
        if self.llm_calls >= self.budget.llm_calls:
            raise BudgetExhausted("llm_calls")
        if self.renames >= self.budget.renames:
            raise BudgetExhausted("renames")
        if self.elapsed >= self.budget.seconds:
            raise BudgetExhausted("seconds")

    def spend_llm(self, n: int = 1) -> None:
        self.check()
        self.llm_calls += n

    def spend_rename(self, n: int = 1) -> None:
        self.check()
        self.renames += n

    def summary(self) -> dict:
        return {
            "llm_calls": f"{self.llm_calls}/{self.budget.llm_calls}",
            "renames": f"{self.renames}/{self.budget.renames}",
            "seconds": f"{self.elapsed:.0f}/{self.budget.seconds:.0f}",
        }
