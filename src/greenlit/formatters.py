"""Output formatters: XML, Markdown, JSON."""

import html
import json
from collections.abc import Callable

from greenlit.sections import SECTIONS


def format_xml(data: dict, task_type: str) -> str:
    lines = [f'<prompt type="{task_type}">']
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
    lines = [f"# {task_type.upper()} PROMPT", ""]
    for s in SECTIONS:
        val = data.get(s.key, "").strip()
        if val:
            lines.append(f"## {s.label}")
            lines.append(val)
            lines.append("")
    return "\n".join(lines)


def format_json(data: dict, task_type: str) -> str:
    obj: dict = {"type": task_type, "sections": {}}
    for s in SECTIONS:
        val = data.get(s.key, "").strip()
        if val:
            obj["sections"][s.key] = val
    return json.dumps(obj, indent=2, sort_keys=True)


FORMATTERS: dict[str, Callable[[dict, str], str]] = {
    "xml": format_xml,
    "markdown": format_markdown,
    "json": format_json,
}


def format_prompt(data: dict, task_type: str, fmt: str) -> str:
    if fmt not in FORMATTERS:
        raise ValueError(f"Unknown format {fmt!r}. Choose from: {', '.join(FORMATTERS)}")
    return FORMATTERS[fmt](data, task_type)
