"""Parse greenlit prompt files (XML / Markdown) back into (task_type, data).

Round-trips against greenlit.formatters: parse(format_xml(data, t)) == (t, data)
for every non-empty section (values compared after .strip()).
"""

import html
import re

from greenlit.sections import SECTIONS

_VALID_KEYS = {s.key for s in SECTIONS}
_LABEL_TO_KEY = {s.label: s.key for s in SECTIONS}

_XML_TYPE = re.compile(r'<prompt\s+type="([^"]+)"')
_XML_OPEN = re.compile(r"^  <(\w+)>$")
_MD_TITLE = re.compile(r"^#\s+(\w+)\s+PROMPT\s*$")
_MD_HEADER = re.compile(r"^##\s+(\w+)\s*$")


def parse_xml(text: str) -> tuple[str, dict[str, str]]:
    """Parse the XML format produced by format_xml."""
    m = _XML_TYPE.search(text)
    task_type = m.group(1) if m else ""

    data: dict[str, str] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        open_m = _XML_OPEN.match(lines[i])
        if not open_m:
            i += 1
            continue
        key = open_m.group(1)
        close = f"  </{key}>"
        body = []
        i += 1
        while i < len(lines) and lines[i] != close:
            # Each content line was indented by 4 spaces by the formatter.
            body.append(lines[i][4:] if lines[i].startswith("    ") else lines[i])
            i += 1
        if key in _VALID_KEYS:
            data[key] = html.unescape("\n".join(body)).strip()
        i += 1
    return task_type, data


def parse_markdown(text: str) -> tuple[str, dict[str, str]]:
    """Parse the Markdown format produced by format_markdown."""
    lines = text.splitlines()
    task_type = ""
    data: dict[str, str] = {}

    current_key: str | None = None
    buf: list[str] = []

    def flush():
        if current_key is not None:
            data[current_key] = "\n".join(buf).strip()

    for line in lines:
        title_m = _MD_TITLE.match(line)
        if title_m:
            task_type = title_m.group(1).lower()
            continue
        header_m = _MD_HEADER.match(line)
        if header_m:
            flush()
            label = header_m.group(1)
            current_key = _LABEL_TO_KEY.get(label)
            buf = []
            continue
        if current_key is not None:
            buf.append(line)
    flush()

    # drop any header we didn't recognise (mapped to None) and empties
    return task_type, {k: v for k, v in data.items() if k and v}


def parse_prompt(text: str) -> tuple[str, dict[str, str]]:
    """Detect format and parse. Returns (task_type, data)."""
    stripped = text.lstrip()
    if stripped.startswith("<prompt"):
        return parse_xml(text)
    if stripped.startswith("#"):
        return parse_markdown(text)
    raise ValueError("Unrecognised greenlit format — expected XML or Markdown.")


def parse_file(path: str) -> tuple[str, dict[str, str]]:
    """Read a file and parse it based on extension, falling back to content sniffing."""
    with open(path) as f:
        text = f.read()
    if path.endswith(".xml"):
        return parse_xml(text)
    if path.endswith(".md"):
        return parse_markdown(text)
    return parse_prompt(text)
