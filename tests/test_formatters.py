"""Unit tests for greenlit.formatters."""

import pytest

from greenlit.formatters import format_markdown, format_prompt, format_xml

SAMPLE = {
    "ask": "Do the thing",
    "goal": "Make it work",
    "context": "Line one\nLine two",
}


# ── format_xml ────────────────────────────────────────────────────────

def test_xml_wraps_in_prompt_tag():
    out = format_xml(SAMPLE, "action")
    assert out.startswith('<prompt type="action" greenlit="0.2">')
    assert out.endswith("</prompt>")


def test_xml_includes_filled_sections():
    out = format_xml(SAMPLE, "review")
    assert "<ask>" in out and "</ask>" in out
    assert "<goal>" in out


def test_xml_omits_empty_sections():
    out = format_xml({"ask": "X", "scope": ""}, "plan")
    assert "<scope>" not in out


def test_xml_indentation_two_spaces():
    out = format_xml({"ask": "X"}, "action")
    lines = out.splitlines()
    tag_line = next(line for line in lines if "<ask>" in line)
    assert tag_line.startswith("  <ask>"), f"expected 2-space indent, got: {tag_line!r}"


def test_xml_multiline_content_indented():
    out = format_xml({"context": "line1\nline2"}, "action")
    assert "    line1" in out
    assert "    line2" in out


def test_xml_escapes_special_chars():
    out = format_xml({"ask": "<b>bold</b> & more"}, "action")
    assert "&lt;b&gt;" in out
    assert "&amp;" in out


# ── format_markdown ───────────────────────────────────────────────────

def test_markdown_heading_includes_task_type():
    out = format_markdown(SAMPLE, "review")
    assert out.startswith("# REVIEW PROMPT")
    assert "<!-- greenlit: 0.2 -->" in out


def test_markdown_uses_section_labels_as_h2():
    out = format_markdown(SAMPLE, "action")
    assert "## ASK" in out
    assert "## GOAL" in out


def test_markdown_omits_empty_sections():
    out = format_markdown({"ask": "X", "context": ""}, "plan")
    assert "## CONTEXT" not in out


def test_markdown_task_type_upper():
    out = format_markdown({}, "debug")
    assert out.startswith("# DEBUG PROMPT")


# ── format_prompt dispatch ────────────────────────────────────────────

def test_format_prompt_dispatches_xml():
    out = format_prompt({"ask": "X"}, "action", "xml")
    assert "<ask>" in out


def test_format_prompt_dispatches_markdown():
    out = format_prompt({"ask": "X"}, "plan", "markdown")
    assert "## ASK" in out


def test_format_prompt_raises_for_unknown_format():
    with pytest.raises(ValueError, match="Unknown format"):
        format_prompt({}, "action", "toml")
