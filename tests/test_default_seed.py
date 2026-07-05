"""Interactive-authoring tests: CONSTRAINT is seeded with the type's defaults."""

import sys
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from greenlit.cli import main, run
from greenlit.guidance import get_default_constraints
from greenlit.parser import parse_file, parse_prompt

ALL_TYPES = ["review", "plan", "action", "debug", "research", "docs"]

_CHROME = [
    "greenlit.cli.show_header",
    "greenlit.cli.show_step_bar",
    "greenlit.cli.show_section_header",
    "greenlit.cli.show_tips",
    "greenlit.cli.show_nav_help",
    "greenlit.cli.show_output",
    "greenlit.cli.show_transition",
    "greenlit.cli.show_task_selector",
]

# ask goal context scope inputs outputs constraint attention done
CONSTRAINT_STEP = 6


def _patch_chrome():
    stack = ExitStack()
    for target in _CHROME:
        stack.enter_context(patch(target))
    stack.enter_context(patch("greenlit.cli.console.print"))
    return stack


def _args(tmp_path, task_type, lite=False):
    return SimpleNamespace(
        type=task_type, name=f"{task_type}-seed", output="xml",
        file=None, dir=str(tmp_path / ".greenlit"), copy=False,
        no_editor=True, lite=lite, stdout=False, private=False,
    )


@pytest.mark.parametrize("task_type", ["review", "plan", "action", "debug", "research", "docs"])
def test_walkthrough_seeds_constraint_defaults(tmp_path, monkeypatch, task_type):
    monkeypatch.chdir(tmp_path)
    args = _args(tmp_path, task_type)
    # skip through all nine sections (keeps the seeded constraint), then save
    seq = ["s"] * 9 + ["save"]
    with _patch_chrome(), patch("greenlit.cli.Prompt.ask", side_effect=seq):
        run(args)

    saved = tmp_path / ".greenlit" / f"{task_type}-seed" / f"{task_type}.xml"
    _, data = parse_file(str(saved))
    assert data.get("constraint", "").split("\n") == get_default_constraints(task_type)


def test_clearing_prefill_yields_empty_constraint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = _args(tmp_path, "action")
    # skip to CONSTRAINT (steps 0-5), open editor and clear it, skip the rest, save
    seq = ["s"] * CONSTRAINT_STEP + ["write"] + ["s", "s"] + ["save"]
    with _patch_chrome(), \
         patch("greenlit.cli.read_multiline", return_value=""), \
         patch("greenlit.cli.Prompt.ask", side_effect=seq):
        run(args)

    saved = tmp_path / ".greenlit" / "action-seed" / "action.xml"
    _, data = parse_file(str(saved))
    assert "constraint" not in data


def test_editing_prefill_replaces_it(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = _args(tmp_path, "action")
    seq = ["s"] * CONSTRAINT_STEP + ["write"] + ["s", "s"] + ["save"]
    with _patch_chrome(), \
         patch("greenlit.cli.read_multiline", return_value="My only rule."), \
         patch("greenlit.cli.Prompt.ask", side_effect=seq):
        run(args)

    saved = tmp_path / ".greenlit" / "action-seed" / "action.xml"
    _, data = parse_file(str(saved))
    assert data["constraint"] == "My only rule."


def test_lite_output_includes_constraint_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = _args(tmp_path, "action", lite=True)
    # lite steps: ask, scope, done — skip all three, then save
    seq = ["s"] * 3 + ["save"]
    with _patch_chrome(), patch("greenlit.cli.Prompt.ask", side_effect=seq):
        run(args)

    saved = tmp_path / ".greenlit" / "action-seed" / "action.xml"
    _, data = parse_file(str(saved))
    assert data.get("constraint", "").split("\n") == get_default_constraints("action")


# ── greenlit new: default / override / opt-out ────────────────────────────────

@pytest.mark.parametrize("task_type", ALL_TYPES)
def test_new_includes_defaults(task_type, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [
        "greenlit", "new", "-t", task_type, "--set", "ask=Do it", "-o", "xml", "--stdout",
    ])
    main()
    _, data = parse_prompt(capsys.readouterr().out)
    assert data.get("constraint", "").split("\n") == get_default_constraints(task_type)


def test_new_explicit_constraint_replaces_defaults(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [
        "greenlit", "new", "-t", "action",
        "--set", "ask=Do it", "--set", "constraint=Only my rule.",
        "-o", "xml", "--stdout",
    ])
    main()
    _, data = parse_prompt(capsys.readouterr().out)
    assert data["constraint"] == "Only my rule."


def test_new_no_default_constraints_opt_out(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [
        "greenlit", "new", "-t", "action",
        "--set", "ask=Do it", "--no-default-constraints",
        "-o", "xml", "--stdout",
    ])
    main()
    _, data = parse_prompt(capsys.readouterr().out)
    assert "constraint" not in data


def test_new_docs_opt_out(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [
        "greenlit", "new", "-t", "docs",
        "--set", "ask=Update docs", "--no-default-constraints",
        "-o", "markdown", "--stdout",
    ])
    main()
    _, data = parse_prompt(capsys.readouterr().out)
    assert "constraint" not in data
