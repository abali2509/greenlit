"""Tests for the docs task type: registration, completeness, round-trip."""

from greenlit.formatters import format_markdown, format_xml
from greenlit.guidance import get_default_constraints, get_guidance
from greenlit.parser import parse_markdown, parse_xml
from greenlit.sections import SECTIONS, TASK_TYPES

SECTION_KEYS = [s.key for s in SECTIONS]


def test_docs_registered_in_task_types():
    assert "docs" in TASK_TYPES
    assert TASK_TYPES["docs"]["label"] == "Docs"
    assert TASK_TYPES["docs"]["desc"].strip()


def test_docs_guidance_covers_every_section():
    guidance = get_guidance("docs")
    missing = [k for k in SECTION_KEYS if k not in guidance]
    assert not missing, f"docs guidance missing: {missing}"
    for key in SECTION_KEYS:
        g = guidance[key]
        assert g.hint.strip()
        assert g.placeholder.strip()
        assert g.tips


def test_docs_default_constraints():
    assert get_default_constraints("docs") == [
        "Modify only documentation files; never change code behavior.",
        "Match the existing documentation's voice and conventions.",
        "Verify that examples and commands in the docs actually run.",
    ]


def test_docs_xml_round_trip():
    data = {"ask": "Update the README", "scope": "README only", "done": "examples run"}
    parsed_type, parsed = parse_xml(format_xml(data, "docs"))
    assert parsed_type == "docs"
    assert parsed == data


def test_docs_markdown_round_trip():
    data = {"ask": "Update the README", "constraint": "docs files only"}
    parsed_type, parsed = parse_markdown(format_markdown(data, "docs"))
    assert parsed_type == "docs"
    assert parsed == data
