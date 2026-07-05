"""Output formatters: XML, Markdown."""

import html
from collections.abc import Callable

from greenlit.sections import SECTIONS

_FORMAT_VERSION = "0.2"


def format_xml(data: dict, task_type: str) -> str:
    lines = [f'<prompt type="{task_type}" greenlit="{_FORMAT_VERSION}">']
    for s in SECTIONS:
        val = data.get(s.key, "").strip()
        if val:
            escaped = html.escape(val)
            indented = escaped.replace("\n", "\n    ")
            lines.append(f"  <{s.key}>")
            lines.append(f"    {indented}")
            lines.append(f"  </{s.key}>")
    lines.append("</prompt>")
    return "\n".join(lines)


def format_markdown(data: dict, task_type: str) -> str:
    lines = [f"# {task_type.upper()} PROMPT", f"<!-- greenlit: {_FORMAT_VERSION} -->", ""]
    for s in SECTIONS:
        val = data.get(s.key, "").strip()
        if val:
            lines.append(f"## {s.label}")
            lines.append(val)
            lines.append("")
    return "\n".join(lines)


FORMATTERS: dict[str, Callable[[dict, str], str]] = {
    "xml": format_xml,
    "markdown": format_markdown,
}


def format_prompt(data: dict, task_type: str, fmt: str) -> str:
    if fmt not in FORMATTERS:
        raise ValueError(f"Unknown format {fmt!r}. Choose from: {', '.join(FORMATTERS)}")
    return FORMATTERS[fmt](data, task_type)
