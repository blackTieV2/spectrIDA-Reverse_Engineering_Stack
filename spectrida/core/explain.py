"""Explain mode: versioned prompt contract, tolerant parser, streaming.

Turns one function's disassembly + call-graph context into a structured,
parseable natural-language explanation. The output contract is designed to
degrade gracefully: a model that ignores the format still yields displayable
text (in ``Explanation.raw``) instead of raising.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import asdict, dataclass, field

from spectrida.core.ollama import _insn_line, stream_generate

EXPLAIN_SYSTEM = (
    "You are an expert reverse engineer. Given disassembly and call-graph "
    "context for ONE function, explain what it does for a working analyst. "
    "Rules: be concrete; cite evidence (strings, constants, callees); admit "
    "uncertainty instead of inventing behaviour; never claim to know the "
    "original source name. Answer in EXACTLY this format:\n"
    "PURPOSE: <one sentence>\n"
    "BEHAVIOR:\n1. <step>\n2. <step>\n"
    "INPUTS: <arguments / globals read, or 'none evident'>\n"
    "OUTPUTS: <return value / globals written, or 'none evident'>\n"
    "SIDE_EFFECTS: <I/O, memory allocation, calls with side effects, or 'none'>\n"
    "SUGGESTED_NAME: <snake_case>\n"
    "CONFIDENCE: high|medium|low - <one clause why>"
)

_MAX_INSNS = 80
_MAX_PSEUDOCODE_CHARS = 4000

_SECTIONS = (
    "PURPOSE",
    "BEHAVIOR",
    "INPUTS",
    "OUTPUTS",
    "SIDE_EFFECTS",
    "SUGGESTED_NAME",
    "CONFIDENCE",
)

_CONFIDENCE_VALUES = {"high", "medium", "low"}


@dataclass
class Explanation:
    """A parsed explanation. All fields optional — the parser never raises."""

    purpose: str = ""
    behavior: list[str] = field(default_factory=list)
    inputs: str = ""
    outputs: str = ""
    side_effects: str = ""
    suggested_name: str = ""
    confidence: str = "unknown"
    confidence_why: str = ""
    raw: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def parse_explanation(text: str) -> Explanation:
    """Tolerantly parse model output into an Explanation.

    Missing sections become empty fields, unknown CONFIDENCE values become
    ``unknown``, prose outside the contract is preserved only in ``raw``.
    """
    expl = Explanation(raw=text)
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        matched = False
        for sec in _SECTIONS:
            # accept "SECTION:" and "section:" headers
            if stripped.upper().startswith(sec + ":"):
                sections.setdefault(sec, [])
                sections[sec].append(stripped[len(sec) + 1 :].strip())
                current = sec
                matched = True
                break
        if not matched and current is not None:
            sections[current].append(stripped)

    def _first(sec: str) -> str:
        return sections.get(sec, [""])[0].strip()

    expl.purpose = _first("PURPOSE")
    expl.inputs = _first("INPUTS")
    expl.outputs = _first("OUTPUTS")
    expl.side_effects = _first("SIDE_EFFECTS")
    expl.suggested_name = _first("SUGGESTED_NAME").split()[0] if _first("SUGGESTED_NAME") else ""

    # BEHAVIOR: numbered steps, one per line, in order
    expl.behavior = [ln for ln in sections.get("BEHAVIOR", []) if ln]

    # CONFIDENCE: "high - because ..." -> value + why. Split on " - " so
    # hyphenated garbage values (e.g. "absolutely-sure") don't eat the why.
    conf_raw = " ".join(sections.get("CONFIDENCE", [])).strip()
    if conf_raw:
        value, _, why = conf_raw.partition(" - ")
        value = value.strip().lower()
        if value in _CONFIDENCE_VALUES:
            expl.confidence = value
        expl.confidence_why = why.strip()

    return expl


def build_explain_prompt(
    insns: list[dict],
    *,
    context_block: str = "",
    pseudocode: str = "",
) -> str:
    """Assemble the user prompt from plain data (no I/O, no graph access)."""
    parts: list[str] = []
    if context_block:
        parts.append(context_block.strip())
    asm_lines = "\n".join(_insn_line(i) for i in insns[:_MAX_INSNS])
    parts.append(f"Assembly:\n{asm_lines}")
    if pseudocode:
        parts.append(f"Pseudocode:\n{pseudocode[:_MAX_PSEUDOCODE_CHARS]}")
    parts.append("Explain this function:")
    return "\n\n".join(parts)


async def stream_explain(
    insns: list[dict],
    *,
    context_block: str = "",
    pseudocode: str = "",
) -> AsyncIterator[str]:
    """Yield explanation tokens as the model writes them."""
    async for tok in stream_generate(
        EXPLAIN_SYSTEM,
        build_explain_prompt(insns, context_block=context_block, pseudocode=pseudocode),
        num_predict=512,
        temperature=0.2,
    ):
        yield tok


async def explain(
    insns: list[dict],
    *,
    context_block: str = "",
    pseudocode: str = "",
) -> Explanation:
    """Non-streaming convenience — returns the parsed Explanation."""
    full = "".join(
        [
            tok
            async for tok in stream_explain(
                insns, context_block=context_block, pseudocode=pseudocode
            )
        ]
    )
    return parse_explanation(full)
