"""Regression pins for the naming path after the stream_generate extraction.

The refactor moved the httpx streaming loop out of stream_name into a shared
transport. These tests pin the naming prompt and parser behaviour so the
extraction cannot silently alter what the model is asked or how its answer
is read.
"""
from __future__ import annotations

from spectrida.core.ollama import _build_prompt, extract_name

_INSNS = [
    {"address": "0x1000", "text": "push ebp"},
    {"address": "0x1001", "text": "mov ebp, esp"},
    {"address": "0x1003", "text": "call 0x1010"},
    {"address": "0x1008", "text": "pop ebp"},
    {"address": "0x1009", "text": "ret"},
]

_EXPECTED_PROMPT = (
    "Calls: sub_1010, printf\n"
    "Called by: main\n"
    "\n"
    "Assembly:\n"
    "            0x1000  push ebp\n"
    "            0x1001  mov ebp, esp\n"
    "            0x1003  call 0x1010\n"
    "            0x1008  pop ebp\n"
    "            0x1009  ret\n"
    "\n"
    "Name this function:"
)


def test_build_prompt_is_byte_identical() -> None:
    got = _build_prompt(_INSNS, ["sub_1010", "printf"], ["main"])
    assert got == _EXPECTED_PROMPT


def test_build_prompt_caps_at_80_instructions() -> None:
    many = [{"address": hex(0x1000 + i * 5), "text": "nop"} for i in range(120)]
    got = _build_prompt(many, [], [])
    assert got.count("nop") == 80
    assert "Calls: none" in got
    assert "Called by: none" in got


def test_build_prompt_mnemonic_fallback() -> None:
    insns = [{"address": "0x2000", "mnemonic": "xor", "op_str": "eax, eax"}]
    got = _build_prompt(insns, [], [])
    assert "xor  eax, eax" in got


def test_extract_name_historical_outputs() -> None:
    # canonical two-line output
    assert extract_name("NAME: compute_hash\nREASON: it xors things") == "compute_hash"
    # name line buried under prose
    assert extract_name("Let me think.\nNAME: parse_header\nREASON: reads fields") == "parse_header"
    # no valid name -> None (batch mode turns this into "")
    assert extract_name("I cannot determine this.") is None
    # non-identifier candidate rejected
    assert extract_name("NAME: 0xbad-name\nREASON: x") is None
