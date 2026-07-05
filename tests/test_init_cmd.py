"""Unit tests for init_cmd.run_init() — verifies both skill files land in the right targets."""

from unittest.mock import patch

from greenlit.init_cmd import run_init


def _run(choice, monkeypatch):
    with patch("greenlit.init_cmd.Prompt.ask", return_value=choice), \
         patch("greenlit.init_cmd.console.print"):
        run_init()


class TestRunInit:
    def test_choice_1_writes_both_skills_to_user_claude(self, tmp_path, monkeypatch):
        monkeypatch.setattr("greenlit.init_cmd._HOME", str(tmp_path))
        _run("1", monkeypatch)
        read = tmp_path / ".claude" / "skills" / "greenlit-Read" / "SKILL.md"
        write = tmp_path / ".claude" / "skills" / "greenlit-Write" / "SKILL.md"
        assert read.exists(), f"Expected greenlit-Read at {read}"
        assert write.exists(), f"Expected greenlit-Write at {write}"
        assert "name: greenlit-Read" in read.read_text()
        assert "name: greenlit-Write" in write.read_text()

    def test_choice_2_writes_both_skills_to_project_claude(self, tmp_path, monkeypatch):
        monkeypatch.setattr("greenlit.init_cmd._HOME", str(tmp_path / "home"))
        monkeypatch.chdir(tmp_path)
        _run("2", monkeypatch)
        read = tmp_path / ".claude" / "skills" / "greenlit-Read" / "SKILL.md"
        write = tmp_path / ".claude" / "skills" / "greenlit-Write" / "SKILL.md"
        assert read.exists()
        assert write.exists()

    def test_choice_3_writes_both_skills_to_github_instructions(self, tmp_path, monkeypatch):
        monkeypatch.setattr("greenlit.init_cmd._HOME", str(tmp_path))
        monkeypatch.chdir(tmp_path)
        _run("3", monkeypatch)
        read = tmp_path / ".github" / "instructions" / "greenlit-read.instructions.md"
        write = tmp_path / ".github" / "instructions" / "greenlit-write.instructions.md"
        assert read.exists(), f"Expected {read}"
        assert write.exists(), f"Expected {write}"

    def test_read_skill_content_contains_frontmatter(self, tmp_path, monkeypatch):
        monkeypatch.setattr("greenlit.init_cmd._HOME", str(tmp_path))
        _run("1", monkeypatch)
        content = (tmp_path / ".claude" / "skills" / "greenlit-Read" / "SKILL.md").read_text()
        assert content.startswith("---"), "Skill file should start with YAML frontmatter"
        assert "name: greenlit-Read" in content

    def test_target_directory_created_if_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr("greenlit.init_cmd._HOME", str(tmp_path))
        monkeypatch.chdir(tmp_path)
        assert not (tmp_path / ".claude").exists()
        _run("1", monkeypatch)
        assert (tmp_path / ".claude" / "skills" / "greenlit-Read").is_dir()
        assert (tmp_path / ".claude" / "skills" / "greenlit-Write").is_dir()
