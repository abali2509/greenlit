"""Round-trip tests: format_* then parse_* must recover (task_type, data)."""

import pytest

from greenlit.formatters import format_markdown, format_xml
from greenlit.parser import parse_file, parse_markdown, parse_prompt, parse_xml

SAMPLES = [
    ("action", {"ask": "Do the thing", "scope": "auth/ only", "done": "pytest passes"}),
    ("review", {"ask": "Review PR", "goal": "Ship safely"}),
    (
        "debug",
        {
            "ask": "Fix silent failure",
            "context": "Line one\nLine two\nLine three",
            "constraint": "No downtime",
        },
    ),
    ("plan", {"ask": "Design API", "attention": "Watch the <edge> & cases"}),
]


@pytest.mark.parametrize("task_type,data", SAMPLES)
def test_xml_round_trip(task_type, data):
    rendered = format_xml(data, task_type)
    parsed_type, parsed_data = parse_xml(rendered)
    assert parsed_type == task_type
    assert parsed_data == data


@pytest.mark.parametrize("task_type,data", SAMPLES)
def test_markdown_round_trip(task_type, data):
    rendered = format_markdown(data, task_type)
    parsed_type, parsed_data = parse_markdown(rendered)
    assert parsed_type == task_type
    assert parsed_data == data


@pytest.mark.parametrize("task_type,data", SAMPLES)
def test_parse_prompt_detects_xml(task_type, data):
    rendered = format_xml(data, task_type)
    assert parse_prompt(rendered) == (task_type, data)


@pytest.mark.parametrize("task_type,data", SAMPLES)
def test_parse_prompt_detects_markdown(task_type, data):
    rendered = format_markdown(data, task_type)
    assert parse_prompt(rendered) == (task_type, data)


def test_xml_escapes_recovered():
    data = {"ask": "<b>bold</b> & 'quoted' \"double\""}
    parsed_type, parsed = parse_xml(format_xml(data, "action"))
    assert parsed["ask"] == data["ask"]


def test_multiline_content_recovered():
    data = {"context": "first\nsecond\nthird"}
    _, parsed = parse_xml(format_xml(data, "action"))
    assert parsed["context"] == "first\nsecond\nthird"


def test_parse_prompt_rejects_unknown_format():
    with pytest.raises(ValueError, match="Unrecognised"):
        parse_prompt("just some random text")


def test_parse_file_xml(tmp_path):
    data = {"ask": "Do it"}
    f = tmp_path / "p.xml"
    f.write_text(format_xml(data, "action"))
    assert parse_file(str(f)) == ("action", data)


def test_parse_file_markdown(tmp_path):
    data = {"ask": "Do it"}
    f = tmp_path / "p.md"
    f.write_text(format_markdown(data, "review"))
    assert parse_file(str(f)) == ("review", data)
