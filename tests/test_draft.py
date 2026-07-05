"""Tests for greenlit draft — the agent-authoring meta-prompt."""

import sys
from unittest.mock import patch

from greenlit.cli import main
from greenlit.draft_meta import build_meta_prompt
from greenlit.sections import SECTIONS

SECTION_KEYS = [s.key for s in SECTIONS]


class TestBuildMetaPrompt:
    def test_contains_user_ask_verbatim(self):
        ask = "Add rate limiting to the public API endpoints"
        meta = build_meta_prompt(ask)
        assert ask in meta

    def test_contains_all_section_keys(self):
        meta = build_meta_prompt("Do a thing")
        for key in SECTION_KEYS:
            assert key in meta, f"meta-prompt missing section key {key!r}"

    def test_mentions_done_requirement(self):
        meta = build_meta_prompt("Do a thing")
        assert "DONE" in meta
        assert "mandatory" in meta.lower()

    def test_explicit_type_used_in_output_path(self):
        meta = build_meta_prompt("Refactor auth", task_type="action")
        assert ".greenlit/action/action.xml" in meta
        assert 'type="action"' in meta

    def test_omitted_type_asks_agent_to_infer(self):
        meta = build_meta_prompt("Refactor auth")
        assert "infer" in meta.lower()

    def test_instructs_to_interview(self):
        meta = build_meta_prompt("Do a thing")
        assert "clarifying question" in meta.lower() or "interview" in meta.lower()


class TestDraftSubcommand:
    def test_draft_prints_meta_to_stdout(self, monkeypatch, capsys):
        ask = "Add caching to the query layer"
        monkeypatch.setattr(sys, "argv", ["greenlit", "draft", ask])
        main()
        out = capsys.readouterr().out
        assert ask in out
        assert "DONE" in out

    def test_draft_with_type(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["greenlit", "draft", "Fix the bug", "-t", "debug"])
        main()
        out = capsys.readouterr().out
        assert 'type="debug"' in out

    def test_draft_copy_message_goes_to_stderr(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["greenlit", "draft", "Do a thing", "-c"])
        with patch("greenlit.cli._copy_to_clipboard", return_value=True):
            main()
        captured = capsys.readouterr()
        assert "Copied to clipboard" in captured.err
        assert "Copied to clipboard" not in captured.out
