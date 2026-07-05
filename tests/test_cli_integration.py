"""Integration and unit tests for cli.py — _resolve_output_path, _provision_output_dir,
path-traversal guards, and a minimal run() walkthrough."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from greenlit.cli import _copy_to_clipboard, _provision_output_dir, _resolve_output_path, main

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

    def test_does_not_touch_gitignore_by_default(self, tmp_path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n")
        greenlit_dir = tmp_path / ".greenlit"
        greenlit_dir.mkdir()
        out_path = str(greenlit_dir / "my-prompt" / "action.xml")
        _provision_output_dir(out_path, str(greenlit_dir), str(tmp_path))
        assert ".greenlit/" not in gitignore.read_text()

    def test_private_flag_adds_greenlit_to_gitignore(self, tmp_path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n")
        greenlit_dir = tmp_path / ".greenlit"
        greenlit_dir.mkdir()
        out_path = str(greenlit_dir / "my-prompt" / "action.xml")
        _provision_output_dir(out_path, str(greenlit_dir), str(tmp_path), private=True)
        assert ".greenlit/" in gitignore.read_text()

    def test_private_does_not_duplicate_gitignore_entry(self, tmp_path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text(".greenlit/\n")
        greenlit_dir = tmp_path / ".greenlit"
        greenlit_dir.mkdir()
        out_path = str(greenlit_dir / "my-prompt" / "action.xml")
        _provision_output_dir(out_path, str(greenlit_dir), str(tmp_path), private=True)
        assert gitignore.read_text().count(".greenlit/") == 1

    def test_private_does_not_add_gitignore_for_custom_root(self, tmp_path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n")
        custom_dir = tmp_path / "output"
        custom_dir.mkdir()
        out_path = str(custom_dir / "my-prompt" / "action.xml")
        _provision_output_dir(out_path, str(custom_dir), str(tmp_path), private=True)
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


# ── _copy_to_clipboard ────────────────────────────────────────────────────────

class TestCopyToClipboard:
    @pytest.mark.parametrize("system,expected_cmd", [
        ("Darwin", ["pbcopy"]),
        ("Windows", ["clip.exe"]),
        ("Linux", ["xclip", "-selection", "clipboard"]),
    ])
    def test_runs_correct_command(self, system, expected_cmd):
        mock_proc = MagicMock(returncode=0)
        with patch("greenlit.cli.platform.system", return_value=system), \
             patch("greenlit.cli.subprocess.run", return_value=mock_proc) as mock_run:
            result = _copy_to_clipboard("hello")
        assert result is True
        called_cmd = mock_run.call_args[0][0]
        assert called_cmd == expected_cmd

    def test_returns_false_when_command_not_found(self):
        with patch("greenlit.cli.platform.system", return_value="Darwin"), \
             patch("greenlit.cli.subprocess.run", side_effect=FileNotFoundError):
            result = _copy_to_clipboard("hello")
        assert result is False

    def test_linux_falls_through_to_next_candidate(self):
        proc_ok = MagicMock(returncode=0)
        proc_fail = MagicMock(returncode=1)
        # xclip fails, xsel succeeds
        with patch("greenlit.cli.platform.system", return_value="Linux"), \
             patch("greenlit.cli.subprocess.run", side_effect=[proc_fail, proc_ok]) as mock_run:
            result = _copy_to_clipboard("hello")
        assert result is True
        assert mock_run.call_count == 2


# ── greenlit new ──────────────────────────────────────────────────────────────

class TestNewSubcommand:
    def test_creates_xml_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", [
            "greenlit", "new", "-t", "action",
            "--set", "ask=Refactor the auth module",
            "--set", "scope=auth/ only",
            "-o", "xml", "-n", "auth-refactor",
        ])
        with patch("greenlit.cli.console.print"):
            main()
        out = tmp_path / ".greenlit" / "auth-refactor" / "action.xml"
        assert out.exists()
        content = out.read_text()
        assert "Refactor the auth module" in content
        assert "<ask>" in content
        assert "<scope>" in content

    def test_creates_markdown_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", [
            "greenlit", "new", "-t", "review",
            "--set", "ask=Review the PR",
            "-o", "markdown", "-n", "pr-review",
        ])
        with patch("greenlit.cli.console.print"):
            main()
        out = tmp_path / ".greenlit" / "pr-review" / "review.md"
        assert out.exists()
        assert "Review the PR" in out.read_text()

    def test_unknown_section_key_exits_1(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", [
            "greenlit", "new", "-t", "action",
            "--set", "bogus=value",
        ])
        with patch("greenlit.cli.console.print"), pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_custom_name_and_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        out_dir = tmp_path / "specs"
        monkeypatch.setattr(sys, "argv", [
            "greenlit", "new", "-t", "plan",
            "--set", "ask=Design the new API",
            "-n", "api-design", "-d", str(out_dir),
        ])
        with patch("greenlit.cli.console.print"):
            main()
        assert (out_dir / "api-design" / "plan.md").exists()

    def test_explicit_file_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        out_file = tmp_path / "my-prompt.xml"
        monkeypatch.setattr(sys, "argv", [
            "greenlit", "new", "-t", "debug",
            "--set", "ask=Fix the crash",
            "-o", "xml", "-f", str(out_file),
        ])
        with patch("greenlit.cli.console.print"):
            main()
        assert out_file.exists()
        assert "Fix the crash" in out_file.read_text()

    def test_no_set_args_creates_empty_prompt(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["greenlit", "new", "-t", "action"])
        with patch("greenlit.cli.console.print"):
            main()
        out = tmp_path / ".greenlit" / "action" / "action.md"
        assert out.exists()

    def test_file_outside_cwd_rejected(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        outside = str(tmp_path.parent / "evil.xml")
        monkeypatch.setattr(sys, "argv", [
            "greenlit", "new", "-t", "action", "-f", outside,
        ])
        with patch("greenlit.cli.console.print"), pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_stdout_flag_writes_to_stdout_not_file(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", [
            "greenlit", "new", "-t", "action",
            "--set", "ask=Do the thing",
            "-o", "xml", "--stdout",
        ])
        main()
        captured = capsys.readouterr()
        assert "<ask>" in captured.out
        assert "Do the thing" in captured.out
        assert not (tmp_path / ".greenlit").exists()

    def test_stdout_markdown_clean_output(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", [
            "greenlit", "new", "-t", "review",
            "--set", "ask=Review auth PR",
            "-o", "markdown", "--stdout",
        ])
        main()
        out = capsys.readouterr().out
        assert "## ASK" in out
        assert "Review auth PR" in out
        assert "<" not in out  # no rich markup leaked
