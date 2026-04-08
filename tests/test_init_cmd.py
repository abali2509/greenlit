"""Unit tests for init_cmd.run_init() — verifies skill file is written to correct targets."""

import os
from unittest.mock import patch

from greenlit.init_cmd import run_init


class TestRunInit:
    def test_choice_1_writes_to_claude_skills(self, tmp_path, monkeypatch):
        monkeypatch.setattr("greenlit.init_cmd._HOME", str(tmp_path))
        with patch("greenlit.init_cmd.Prompt.ask", return_value="1"), \
             patch("greenlit.init_cmd.console.print"):
            run_init()
        dest = tmp_path / ".claude" / "skills" / "greenlit-Read" / "SKILL.md"
        assert dest.exists(), f"Expected skill file at {dest}"
        content = dest.read_text()
        assert "greenlit" in content.lower()

    def test_choice_2_writes_to_github(self, tmp_path, monkeypatch):
        monkeypatch.setattr("greenlit.init_cmd._HOME", str(tmp_path))
        with patch("greenlit.init_cmd.Prompt.ask", return_value="2"), \
             patch("greenlit.init_cmd.console.print"):
            run_init()
        dest = tmp_path / ".github" / "read-greenlit-prompt.md"
        assert dest.exists(), f"Expected skill file at {dest}"
        content = dest.read_text()
        assert "greenlit" in content.lower()

    def test_skill_content_contains_frontmatter(self, tmp_path, monkeypatch):
        monkeypatch.setattr("greenlit.init_cmd._HOME", str(tmp_path))
        with patch("greenlit.init_cmd.Prompt.ask", return_value="1"), \
             patch("greenlit.init_cmd.console.print"):
            run_init()
        dest = tmp_path / ".claude" / "skills" / "greenlit-Read" / "SKILL.md"
        content = dest.read_text()
        assert content.startswith("---"), "Skill file should start with YAML frontmatter"
        assert "name: greenlit-Read" in content

    def test_target_directory_created_if_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr("greenlit.init_cmd._HOME", str(tmp_path))
        assert not (tmp_path / ".claude").exists()
        with patch("greenlit.init_cmd.Prompt.ask", return_value="1"), \
             patch("greenlit.init_cmd.console.print"):
            run_init()
        assert (tmp_path / ".claude" / "skills" / "greenlit-Read").is_dir()
