from spectrida import config


def test_env_override(monkeypatch):
    monkeypatch.setenv("SPECTRIDA_MODEL", "my-model")
    assert config.ollama_model() == "my-model"


def test_defaults():
    assert config.ollama_url().startswith("http")
    assert config.pipeline_workers() == 16


def test_onboarded_marker(tmp_path, monkeypatch):
    monkeypatch.delenv("SPECTRIDA_NO_ONBOARD", raising=False)
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(config, "_ONBOARD_MARKER", tmp_path / ".onboarded")
    assert config.onboarded() is False
    config.set_onboarded()
    assert config.onboarded() is True


def test_env_forces_skip(monkeypatch):
    monkeypatch.setenv("SPECTRIDA_NO_ONBOARD", "1")
    assert config.onboarded() is True



def test_mcp_pinned_below_2():
    """mcp 2.x removed mcp.server.fastmcp (renamed MCPServer) — the whole
    MCP surface imports FastMCP from the v1 path. pyproject must pin <2
    (bit live on the BlackTie machine 2026-08-30: `pip install -e ".[graph]"`
    pulled mcp 2.1.1 and every MCP tool import broke)."""
    import pathlib
    text = (pathlib.Path(__file__).parent.parent / "pyproject.toml").read_text()
    graph_line = next(l for l in text.splitlines()
                      if l.strip().startswith("graph = ["))
    assert 'mcp>=1.0,<2' in graph_line
