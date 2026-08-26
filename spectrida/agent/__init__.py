"""Bounded agent loop for autonomous naming passes.

The loop reuses the same seams the MCP tools wrap (explain, rename,
verify, baseline) via plain injected async callables — no sockets, no
live Ollama required for tests. Budgets are hard caps; convergence
(coverage delta < 2% over 3 iterations) is the normal stop signal.

Workspace doctrine: all OKF records written by the agent are drafts.
"""
from spectrida.agent.budget import Budget, BudgetTracker, BudgetExhausted
from spectrida.agent.loop import AgentLoop, LoopResult
from spectrida.agent.planner import Action, Planner
from spectrida.agent.report import RunReport

__all__ = [
    "Action", "AgentLoop", "Budget", "BudgetExhausted", "BudgetTracker",
    "LoopResult", "Planner", "RunReport",
]
