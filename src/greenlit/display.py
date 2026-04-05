"""Rich-based terminal display and multi-line input."""

import os
import shutil
import subprocess
import sys
import tempfile

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from greenlit.formatters import FORMATTERS
from greenlit.sections import SECTIONS, TASK_TYPES

console = Console()

# ── Colour constants ──────────────────────────────────────────────────
ACCENT = "bright_green"
DIM = "bright_black"
MUTED = "grey62"
GREEN = "green3"
ORANGE = "dark_orange"
LABEL = "bright_cyan"


# ── Multi-line input ──────────────────────────────────────────────────

def read_multiline(
    placeholder: str = "",
    default: str = "",
    hint: str = "",
    tips: list[str] | None = None,
) -> str:
    """Read multi-line input. Blank line to finish."""
    if hint:
        console.print(f"  [{DIM}]{hint}[/{DIM}]")
    if tips:
        for tip in tips:
            console.print(f"  [{DIM}]→ {tip}[/{DIM}]")
    if hint or tips:
        console.print()
    console.print(f"  [{DIM}]Type your content below. Blank line to finish.[/{DIM}]")
    if placeholder:
        short = placeholder[:120] + ("..." if len(placeholder) > 120 else "")
        console.print(f"  [{DIM}]e.g. {short}[/{DIM}]")
    if default:
        console.print(f"  [{DIM}]defaults pre-filled — edit or replace:[/{DIM}]")
    console.print()

    lines = list(default.splitlines()) if default else []
    for pre in lines:
        console.print(f"  [{MUTED}]│ {pre}[/]")
    if lines:
        console.print()

    while True:
        try:
            line = input("  │ ")
        except (EOFError, KeyboardInterrupt):
            break
        if line == "" and lines:
            break
        lines.append(line)

    return "\n".join(lines).strip()


def show_transition():
    """Clear the screen including scrollback buffer."""
    sys.stdout.write("\033[H\033[2J\033[3J")
    sys.stdout.flush()


_HINT_START = "<!-- greenlit-hint"
_HINT_END = "-->"


def _build_hint_block(hint: str, tips: list[str]) -> str:
    lines = [_HINT_START]
    for line in hint.splitlines():
        lines.append(line)
    if tips:
        lines.append("")
        for tip in tips:
            lines.append(f"→ {tip}")
    lines.append(_HINT_END)
    lines.append("")
    return "\n".join(lines)


def _strip_hint_block(text: str) -> str:
    lines = text.splitlines()
    out, inside = [], False
    for line in lines:
        if line.strip().startswith(_HINT_START):
            inside = True
            continue
        if inside:
            if line.strip() == _HINT_END:
                inside = False
            continue
        out.append(line)
    return "\n".join(out).strip()


def open_editor(
    placeholder: str = "",
    default: str = "",
    hint: str = "",
    tips: list[str] | None = None,
) -> str:
    """Open the user's preferred editor for section content. Falls back to read_multiline."""
    editor = (
        os.environ.get("VISUAL")
        or os.environ.get("EDITOR")
        or shutil.which("nvim")
        or shutil.which("vim")
    )
    if not editor:
        return read_multiline(placeholder, default, hint=hint, tips=tips)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, prefix="greenlit_"
    ) as f:
        if hint or tips:
            f.write(_build_hint_block(hint, tips or []))
        if default:
            f.write(default)
        tmp_path = f.name

    try:
        subprocess.run([editor, tmp_path], check=False)
        with open(tmp_path) as f:
            raw = f.read()
        return _strip_hint_block(raw)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


# ── Display helpers ───────────────────────────────────────────────────

def show_header():
    console.print()
    console.print(
        Panel(
            Text("greenlit", style=f"bold {ACCENT}", justify="center"),
            subtitle="structure prompts before you burn tokens",
            subtitle_align="center",
            border_style=DIM,
            padding=(1, 4),
        )
    )
    console.print()


def show_task_selector(task_types: dict) -> str:
    table = Table(
        box=box.SIMPLE_HEAVY,
        border_style=DIM,
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("key", style=f"bold {ACCENT}", width=10)
    table.add_column("type", style="bold", width=12)
    table.add_column("desc", style=MUTED)

    short_to_full = {}
    all_choices = []
    for key, t in task_types.items():
        short = t.get("short", "")
        icon = t.get("icon", "")
        label = f"{icon} {t['label']}".strip() if icon else t["label"]
        display_key = short if short else key
        table.add_row(display_key, label, t["desc"])
        all_choices.append(key)
        if short:
            short_to_full[short] = key
            all_choices.append(short)

    console.print(table)
    console.print()

    answer = Prompt.ask(
        f"  [{ACCENT}]Task type[/{ACCENT}]",
        choices=all_choices,
        show_choices=False,
    )
    return short_to_full.get(answer, answer)


def show_step_bar(current: int, data: dict):
    parts = []
    for i, s in enumerate(SECTIONS):
        filled = bool(data.get(s.key, "").strip())
        if i == current:
            parts.append(f"[bold {ACCENT}]▸ {s.label}[/]")
        elif filled:
            parts.append(f"[{GREEN}]✓ {s.label}[/]")
        else:
            parts.append(f"[{DIM}]  {s.label}[/]")

    console.print("  " + "  ".join(parts))
    console.print()


def show_section_header(section, guidance, step: int):
    g = guidance

    console.print(
        f"  [{ACCENT} bold]{section.label}[/]  [{DIM}]{step + 1}/{len(SECTIONS)}[/]"
    )
    console.print(f"  [{MUTED}]{section.tagline}[/]")
    console.print()
    console.print(
        Panel(
            g.hint,
            border_style=DIM,
            padding=(0, 2),
            width=min(console.width - 4, 90),
        )
    )
    console.print()


def show_tips(tips: list[str]):
    console.print(f"  [{DIM}]what makes this section land[/]")
    for tip in tips:
        console.print(f"  [{DIM}]→[/] [{MUTED}]{tip}[/]")
    console.print()


def show_output(data: dict, task_type: str, fmt: str):
    formatter = FORMATTERS[fmt]
    output = formatter(data, task_type)

    filled = sum(1 for s in SECTIONS if data.get(s.key, "").strip())
    label = TASK_TYPES[task_type]["label"]

    console.print()
    console.print(
        Rule(
            f" {label} prompt  ·  {filled}/{len(SECTIONS)} sections  ·  {fmt} ",
            style=ACCENT,
        )
    )
    console.print()
    console.print(
        Panel(
            output,
            border_style=DIM,
            padding=(1, 2),
        )
    )


def show_nav_help():
    console.print(
        f"  [{DIM}]commands: (n)ext  (b)ack  (s)kip  (p)review  (e)dit  (q)uit[/]"
    )
    console.print()
