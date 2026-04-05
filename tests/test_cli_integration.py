"""Integration and unit tests for cli.py — _resolve_output_path, _provision_output_dir,
path-traversal guards, and a minimal run() walkthrough."""

import os
import sys
from unittest.mock import patch

import pytest

from greenlit.cli import _provision_output_dir, _resolve_output_path

# ── _resolve_output_path ──────────────────────────────────────────────────────

class TestResolveOutputPath:
    def test_base_path_no_collision(self, tmp_path):
        result = _resolve_output_path(str(tmp_path), "my-prompt", "action", "xml")
        expected = os.path.join(str(tmp_path), "my-prompt", "action.xml")
        assert result == expected

    def test_markdown_uses_md_extension(self, tmp_path):
        result = _resolve_output_path(str(tmp_path), "my-prompt", "plan", "markdown")
        assert result.endswith("plan.md")

    def test_collision_adds_suffix_2(self, tmp_path):
        subdir = tmp_path / "my-prompt"
        subdir.mkdir()
        (subdir / "action.xml").touch()
        result = _resolve_output_path(str(tmp_path), "my-prompt", "action", "xml")
        assert result.endswith("action_2.xml")

    def test_collision_increments_to_3(self, tmp_path):
        subdir = tmp_path / "my-prompt"
        subdir.mkdir()
        (subdir / "action.xml").touch()
        (subdir / "action_2.xml").touch()
        result = _resolve_output_path(str(tmp_path), "my-prompt", "action", "xml")
        assert result.endswith("action_3.xml")


# ── _provision_output_dir ─────────────────────────────────────────────────────

class TestProvisionOutputDir:
    def test_creates_output_directory(self, tmp_path):
        out_path = str(tmp_path / "sub" / "dir" / "file.xml")
        _provision_output_dir(out_path, str(tmp_path), str(tmp_path))
        assert os.path.isdir(str(tmp_path / "sub" / "dir"))

    def test_adds_greenlit_to_gitignore_when_default_root(self, tmp_path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n")
        greenlit_dir = tmp_path / ".greenlit"
        greenlit_dir.mkdir()
        out_path = str(greenlit_dir / "my-prompt" / "action.xml")
        _provision_output_dir(out_path, str(greenlit_dir), str(tmp_path))
        assert ".greenlit/" in gitignore.read_text()

    def test_does_not_duplicate_gitignore_entry(self, tmp_path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text(".greenlit/\n")
        greenlit_dir = tmp_path / ".greenlit"
        greenlit_dir.mkdir()
        out_path = str(greenlit_dir / "my-prompt" / "action.xml")
        _provision_output_dir(out_path, str(greenlit_dir), str(tmp_path))
        assert gitignore.read_text().count(".greenlit/") == 1

    def test_does_not_add_gitignore_for_custom_root(self, tmp_path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n")
        custom_dir = tmp_path / "output"
        custom_dir.mkdir()
        out_path = str(custom_dir / "my-prompt" / "action.xml")
        _provision_output_dir(out_path, str(custom_dir), str(tmp_path))
        assert ".greenlit/" not in gitignore.read_text()


# ── Path-traversal guards ─────────────────────────────────────────────────────

class TestPathTraversalGuards:
    def _run_main(self, argv, monkeypatch):
        """Invoke cli.main() with a given argv list."""
        monkeypatch.setattr(sys, "argv", argv)
        from greenlit.cli import main
        return main

    def test_file_outside_cwd_is_rejected(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        outside = str(tmp_path.parent / "evil.xml")
        monkeypatch.setattr(sys, "argv", ["greenlit", "--file", outside])
        from greenlit.cli import main
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_dir_outside_cwd_is_rejected(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        outside = str(tmp_path.parent / "evil_dir")
        monkeypatch.setattr(sys, "argv", ["greenlit", "--dir", outside])
        from greenlit.cli import main
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_file_inside_cwd_is_accepted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        inside = str(tmp_path / "out.xml")
        monkeypatch.setattr(sys, "argv", ["greenlit", "-t", "action", "--file", inside])
        from greenlit.cli import main
        # Guard should pass; abort the interactive loop immediately via KeyboardInterrupt
        with patch("greenlit.cli.show_header"), \
             patch("greenlit.cli.Prompt.ask", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0  # KeyboardInterrupt exits 0, not 1
