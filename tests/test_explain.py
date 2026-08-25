"""Tests for the explain prompt contract (tp-2026-08-25-001)."""
from __future__ import annotations

import pytest

from spectrida.core.explain import (
    Explanation,
    build_context_block,
    build_explain_prompt,
    extract_strings_from_insns,
    parse_explanation,
)

WELL_FORMED = """PURPOSE: Computes a factorial recursively.
BEHAVIOR:
1. Compares n against 1.
2. Recurses with n-1.
3. Multiplies the result by n.
INPUTS: n in ecx (fastcall)
OUTPUTS: factorial(n) in eax
SIDE_EFFECTS: none
SUGGESTED_NAME: factorial
CONFIDENCE: high - self-call and multiply pattern are unambiguous
"""


def test_parse_well_formed_round_trip() -> None:
    e = parse_explanation(WELL_FORMED)
    assert e.purpose == "Computes a factorial recursively."
    assert e.behavior == [
        "1. Compares n against 1.",
        "2. Recurses with n-1.",
        "3. Multiplies the result by n.",
    ]
    assert e.inputs == "n in ecx (fastcall)"
    assert e.outputs == "factorial(n) in eax"
    assert e.side_effects == "none"
    assert e.suggested_name == "factorial"
    assert e.confidence == "high"
    assert e.confidence_why == "self-call and multiply pattern are unambiguous"
    assert e.raw == WELL_FORMED
    d = e.to_dict()
    assert d["confidence"] == "high" and isinstance(d["behavior"], list)


def test_parse_missing_sections_never_raises() -> None:
    e = parse_explanation("PURPOSE: does something\nCONFIDENCE: low - unclear")
    assert e.purpose == "does something"
    assert e.behavior == [] and e.inputs == "" and e.suggested_name == ""
    assert e.confidence == "low"


def test_parse_lowercase_headers_accepted() -> None:
    e = parse_explanation("purpose: adds two numbers\nconfidence: high - trivial")
    assert e.purpose == "adds two numbers"
    assert e.confidence == "high"


def test_parse_prose_before_purpose_ignored_but_kept_raw() -> None:
    text = "Let me look at this function carefully.\nPURPOSE: parses a header"
    e = parse_explanation(text)
    assert e.purpose == "parses a header"
    assert "Let me look" in e.raw


def test_parse_garbage_confidence_becomes_unknown() -> None:
    e = parse_explanation("PURPOSE: x\nCONFIDENCE: absolutely-sure - trust me")
    assert e.confidence == "unknown"
    assert e.confidence_why == "trust me"


def test_parse_total_garbage_is_safe() -> None:
    e = parse_explanation("the model had a bad day and wrote a poem")
    assert e == Explanation(raw="the model had a bad day and wrote a poem")


def _mk_insns(n: int) -> list[dict]:
    return [{"address": hex(0x1000 + i * 4), "text": f"insn_{i}"} for i in range(n)]


def test_prompt_caps_at_80_instructions() -> None:
    p = build_explain_prompt(_mk_insns(200))
    assert "insn_79" in p and "insn_80" not in p


def test_prompt_pseudocode_cap() -> None:
    p = build_explain_prompt(_mk_insns(1), pseudocode="x" * 9000)
    assert len(p) < 9000
    assert "x" * 4000 in p and "x" * 4001 not in p


def test_prompt_includes_context_block_and_ordering() -> None:
    p = build_explain_prompt(
        _mk_insns(2), context_block="Callers: main", pseudocode="int f(){return 1;}"
    )
    assert p.index("Callers: main") < p.index("Assembly:") < p.index("Pseudocode:")
    assert p.rstrip().endswith("Explain this function:")


def test_prompt_omits_empty_sections() -> None:
    p = build_explain_prompt(_mk_insns(1))
    assert "Pseudocode:" not in p
    assert "Assembly:" in p


@pytest.mark.asyncio
async def test_stream_explain_uses_transport(monkeypatch) -> None:
    """stream_explain must route through stream_generate with the contract system prompt."""
    captured = {}

    async def fake_generate(system, prompt, *, num_predict, temperature):
        captured.update(system=system, prompt=prompt, num_predict=num_predict)
        for tok in ["PURPOSE: ", "adds", "\nCONFIDENCE: high - trivial"]:
            yield tok

    monkeypatch.setattr("spectrida.core.explain.stream_generate", fake_generate)
    from spectrida.core import explain as explain_mod

    full = "".join([t async for t in explain_mod.stream_explain(_mk_insns(2))])
    assert "PURPOSE: adds" in full
    assert captured["num_predict"] == 512
    assert "expert reverse engineer" in captured["system"]
    assert "Explain this function:" in captured["prompt"]


@pytest.mark.asyncio
async def test_explain_error_propagates(monkeypatch) -> None:
    async def boom(system, prompt, *, num_predict, temperature):
        raise RuntimeError("model not found")
        yield  # pragma: no cover

    monkeypatch.setattr("spectrida.core.explain.stream_generate", boom)
    from spectrida.core import explain as explain_mod

    with pytest.raises(RuntimeError, match="model not found"):
        _ = [t async for t in explain_mod.stream_explain(_mk_insns(1))]


def test_extract_strings_from_insns() -> None:
    insns = [
        {"text": 'lea     rcx, off_140032000   ; "result=%d"'},
        {"text": "call    printf"},
        {"text": 'lea     rdx, off_140032020   ; "result=%d"'},  # dup
    ]
    assert extract_strings_from_insns(insns) == ["result=%d"]
    assert extract_strings_from_insns([]) == []


def test_build_context_block() -> None:
    block = build_context_block(["main"], ["printf", "add"], ["result=%d"])
    assert "Calls: printf, add" in block
    assert "Called by: main" in block
    assert "Strings: result=%d" in block
    # empty variants degrade to 'none'
    assert "Calls: none" in build_context_block([], [])


@pytest.mark.asyncio
async def test_demo_backend_explain_stream_parses() -> None:
    from spectrida.core.backend import DemoBackend

    b = DemoBackend()
    addr = 0x1400013A0
    insns = await b.disasm(addr)
    full = "".join([t async for t in b.stream_explain(addr, insns, "", "")])
    e = parse_explanation(full)
    assert e.purpose
    assert e.confidence in {"high", "medium", "low"}
    assert e.suggested_name.isidentifier()


@pytest.mark.asyncio
async def test_facade_stream_explain_demo() -> None:
    from spectrida.api import IDADatabase
    from spectrida.core.backend import DemoBackend

    db = IDADatabase(DemoBackend())
    full = "".join([t async for t in db.stream_explain(0x1400013A0)])
    e = parse_explanation(full)
    assert e.purpose and e.confidence in {"high", "medium", "low"}
