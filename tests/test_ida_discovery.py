"""IDA directory resolution: config.toml-aware, idapro.py subdir search.

Regression tests for the live-acceptance failure where onboard was green
(config.toml set) but all 16 shard workers died with
ModuleNotFoundError: No module named 'idapro' — the pipeline read only
the SPECTRIDA_IDALIB env var and expected idapro.py at the install root.
"""
from __future__ import annotations

import os

from spectrida.analysis.parallel_analyze import _find_idapro_dir, _ida_dir


class TestIdaDir:
    def test_env_var_wins(self, monkeypatch):
        monkeypatch.setenv("SPECTRIDA_IDALIB", "/opt/my-ida")
        assert _ida_dir() == "/opt/my-ida"

    def test_config_toml_used_when_env_absent(self, monkeypatch, tmp_path):
        monkeypatch.delenv("SPECTRIDA_IDALIB", raising=False)
        import spectrida.config as config
        monkeypatch.setattr(config, "_cfg",
                            {"ida": {"idalib": str(tmp_path / "ida-portable")}})
        assert _ida_dir() == str(tmp_path / "ida-portable")

    def test_falls_back_to_default_guess(self, monkeypatch):
        monkeypatch.delenv("SPECTRIDA_IDALIB", raising=False)
        import spectrida.config as config
        from spectrida.analysis.parallel_analyze import _default_ida_dir
        monkeypatch.setattr(config, "_cfg", {})
        # Empty config → whatever the platform guess is ("" on bare Linux,
        # the Windows default path on win32). Just not the config value.
        assert _ida_dir() == _default_ida_dir()


class TestFindIdaproDir:
    def test_root_layout(self, tmp_path):
        (tmp_path / "idapro.py").write_text("#")
        assert _find_idapro_dir(str(tmp_path)) == str(tmp_path)

    def test_subdir_layout(self, tmp_path):
        sub = tmp_path / "python"
        sub.mkdir()
        (sub / "idapro.py").write_text("#")
        assert _find_idapro_dir(str(tmp_path)) == str(sub)

    def test_two_levels_deep(self, tmp_path):
        sub = tmp_path / "idalib" / "python"
        sub.mkdir(parents=True)
        (sub / "idapro.py").write_text("#")
        assert _find_idapro_dir(str(tmp_path)) == str(sub)

    def test_missing_falls_back_to_root(self, tmp_path):
        assert _find_idapro_dir(str(tmp_path)) == str(tmp_path)

    def test_empty_dir_passthrough(self):
        assert _find_idapro_dir("") == ""
