"""Tests for tp-002a: OKF crash cards + dynamic-evidence TUI markers."""
from __future__ import annotations

import pytest

from spectrida.okf_bridge import write_crash_card

_CRASH_RESULT = {
    "verdict": "candidate_crash",
    "unique_crashes": 2,
    "rounds": 400,
    "blocks": 14,
    "seeds_used": 3,
    "seed_source": "seeds_dir",
    "crash_inputs": {"wild_write@0xdeadbeef": "41414141"},
    "status_counts": {"crash": 2, "clean": 398},
    "name": "parse_header",
}


def test_crash_card_written_for_candidate_crash(tmp_path) -> None:
    card = write_crash_card(tmp_path, binary="target", addr=0x1000,
                            run_id="run01", result=_CRASH_RESULT)
    assert card is not None and card.exists()
    body = card.read_text(encoding="utf-8")
    assert "status: draft" in body                 # draft-only per doctrine
    assert "phantomrt-alpha" in body               # provenance class
    assert "parse_header" in body and "0x1000" in body
    assert "wild_write@0xdeadbeef" in body         # evidence preserved
    assert "run01" in body


def test_no_card_for_non_crash_verdicts(tmp_path) -> None:
    for verdict in ("exercised_clean", "needs_state", "inconclusive"):
        r = dict(_CRASH_RESULT, verdict=verdict)
        assert write_crash_card(tmp_path, binary="b", addr=0x2000,
                                run_id="r", result=r) is None


def test_card_dedupes_per_addr_and_run(tmp_path) -> None:
    first = write_crash_card(tmp_path, binary="b", addr=0x3000,
                             run_id="same", result=_CRASH_RESULT)
    again = write_crash_card(tmp_path, binary="b", addr=0x3000,
                             run_id="same", result=_CRASH_RESULT)
    assert first is not None and again is None
    # different run -> new card
    other = write_crash_card(tmp_path, binary="b", addr=0x3000,
                             run_id="other", result=_CRASH_RESULT)
    assert other is not None and other != first


def test_card_survives_unwritable_root(tmp_path) -> None:
    # best-effort: I/O failure returns None, never raises
    blocked = tmp_path / "file-not-dir"
    blocked.write_text("x")
    assert write_crash_card(blocked, binary="b", addr=0x1, run_id="r",
                            result=_CRASH_RESULT) is None


@pytest.mark.asyncio
async def test_demo_backend_dyn_flags() -> None:
    from spectrida.core.backend import DemoBackend

    flags = await DemoBackend().dyn_flags([0x1400013A0, 0x140001100, 0x140001600])
    assert flags[0x1400013A0] == "✖"   # crash
    assert flags[0x140001100] == "▶"   # executed
    assert flags[0x140001600] == "?"   # needs_state


@pytest.mark.asyncio
async def test_base_backend_dyn_flags_default_empty() -> None:
    from spectrida.core.backend import Backend

    assert await Backend().dyn_flags([0x1000]) == {}


def test_funclist_marker_render() -> None:
    from spectrida.tui.widgets.funclist import FuncList

    fl = FuncList()
    fl.set_functions([{"name": "main", "start": 0x1000, "end": 0x1010, "size": 16},
                      {"name": "sub_2000", "start": 0x2000, "end": 0x2010, "size": 16}])
    fl.set_dyn_flags({0x1000: "✖"})
    rendered = fl.render().plain
    assert "✖" in rendered
    # function without flags gets a blank marker cell, not a crash
    assert rendered.count("✖") == 1


def test_funclist_blank_flags_render_plain() -> None:
    from spectrida.tui.widgets.funclist import FuncList

    fl = FuncList()
    fl.set_functions([{"name": "main", "start": 0x1000, "end": 0x1010, "size": 16}])
    fl.set_dyn_flags({})
    rendered = fl.render().plain
    assert "✖" not in rendered and "▶" not in rendered
