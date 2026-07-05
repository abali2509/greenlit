"""Tests for greenlit review — stepping through a drafted prompt."""

import sys
from unittest.mock import patch

import pytest

from greenlit.cli import main
from greenlit.formatters import format_xml
from greenlit.parser import parse_file

_CHROME = [
    "greenlit.cli.show_header",
    "greenlit.cli.show_step_bar",
    "greenlit.cli.show_section_header",
    "greenlit.cli.show_nav_help",
    "greenlit.cli.show_output",
    "greenlit.cli.show_transition",
]


def _patch_chrome():
    from contextlib import ExitStack
    stack = ExitStack()
    for target in _CHROME:
        stack.enter_context(patch(target))
    stack.enter_context(patch("greenlit.cli.console.print"))
    return stack


class TestReviewSubcommand:
    def test_missing_file_exits_1(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["greenlit", "review", str(tmp_path / "nope.xml")])
        with patch("greenlit.cli.console.print"), pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1

    def test_review_preserves_prefilled_data_on_save(self, tmp_path, monkeypatch):
        data = {"ask": "Refactor auth", "scope": "auth/ only", "done": "pytest passes"}
        prompt_dir = tmp_path / ".greenlit" / "auth-refactor"
        prompt_dir.mkdir(parents=True)
        f = prompt_dir / "action.xml"
        f.write_text(format_xml(data, "action"))

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["greenlit", "review", str(f), "--no-editor"])
        # skip through all 9 sections (preserving prefilled data), then save
        seq = ["s"] * 9 + ["save"]
        with _patch_chrome(), patch("greenlit.cli.show_tips"), \
             patch("greenlit.cli.Prompt.ask", side_effect=seq):
            main()

        parsed_type, parsed = parse_file(str(f))
        assert parsed_type == "action"
        assert parsed == data

    def test_review_uses_review_framing(self, tmp_path, monkeypatch):
        data = {"ask": "Refactor auth"}
        f = tmp_path / ".greenlit" / "x" / "action.xml"
        f.parent.mkdir(parents=True)
        f.write_text(format_xml(data, "action"))

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["greenlit", "review", str(f), "--no-editor"])
        seq = ["s"] * 9 + ["quit"]
        with _patch_chrome(), patch("greenlit.cli.show_tips") as mock_tips, \
             patch("greenlit.cli.Prompt.ask", side_effect=seq):
            main()

        # every show_tips call during review must pass review=True
        assert mock_tips.call_count > 0
        assert all(call.kwargs.get("review") is True for call in mock_tips.call_args_list)

    def test_review_markdown_file(self, tmp_path, monkeypatch):
        from greenlit.formatters import format_markdown
        data = {"ask": "Review the PR", "done": "checklist complete"}
        f = tmp_path / ".greenlit" / "pr" / "review.md"
        f.parent.mkdir(parents=True)
        f.write_text(format_markdown(data, "review"))

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["greenlit", "review", str(f), "--no-editor"])
        seq = ["s"] * 9 + ["save"]
        with _patch_chrome(), patch("greenlit.cli.show_tips"), \
             patch("greenlit.cli.Prompt.ask", side_effect=seq):
            main()

        parsed_type, parsed = parse_file(str(f))
        assert parsed_type == "review"
        assert parsed == data
