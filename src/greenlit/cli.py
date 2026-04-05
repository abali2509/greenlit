"""CLI entry point: argparse, main loop."""

import argparse
import os
import platform
import subprocess
import sys

from rich.prompt import Confirm, Prompt

from greenlit.display import (
    ACCENT,
    DIM,
    GREEN,
    MUTED,
    ORANGE,
    console,
    read_multiline,
    show_header,
    show_nav_help,
    show_output,
    show_section_header,
    show_step_bar,
    show_task_selector,
    show_tips,
)
from greenlit.formatters import FORMATTERS
from greenlit.guidance import get_guidance
from greenlit.sections import SECTIONS, TASK_TYPES


def _copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard. Returns True on success."""
    system = platform.system()
    if system == "Darwin":
        cmd = ["pbcopy"]
    elif system == "Windows":
        cmd = ["clip.exe"]
    else:
        cmd = ["xclip", "-selection", "clipboard"]
    try:
        proc = subprocess.run(cmd, input=text.encode(), capture_output=True)
        return proc.returncode == 0
    except FileNotFoundError:
        return False


def run(args, task_types: dict | None = None):
    if task_types is None:
        task_types = TASK_TYPES

    show_header()

    # Task type selection
    if args.type and args.type in task_types:
        task_type = args.type
        console.print(f"  [{GREEN}]Task type:[/] {task_types[task_type]['label']}")
        console.print()
    else:
        task_type = show_task_selector(task_types)

    from rich.rule import Rule
    console.print(
        Rule(
            f" {task_types[task_type]['label']} walkthrough ",
            style=ACCENT,
        )
    )
    console.print()

    data: dict[str, str] = {}
    step = 0

    while True:
        if step >= len(SECTIONS):
            fmt = args.output
            show_output(data, task_type, fmt)
            console.print()

            while True:
                action = Prompt.ask(
                    f"  [{ACCENT}]Action[/{ACCENT}]",
                    choices=["xml", "markdown", "json", "save", "edit", "quit"],
                    default="save",
                    show_choices=True,
                )

                if action in FORMATTERS:
                    fmt = action
                    show_output(data, task_type, fmt)
                    console.print()
                elif action == "save":
                    ext = fmt if fmt != "markdown" else "md"
                    filename = args.file or f"greenlit_{task_type}.{ext}"
                    output = FORMATTERS[fmt](data, task_type)
                    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
                    with open(filename, "w") as f:
                        f.write(output)
                    console.print(f"  [{GREEN}]Saved to {filename}[/]")

                    if getattr(args, "copy", False):
                        if _copy_to_clipboard(output):
                            console.print(f"  [{GREEN}]Copied to clipboard[/]")
                        else:
                            msg = "Warning: no clipboard tool found (pbcopy/xclip/clip.exe)"
                            console.print(f"  [{ORANGE}]{msg}[/]")

                    console.print()
                    return
                elif action == "edit":
                    for i, s in enumerate(SECTIONS):
                        filled = "✓" if data.get(s.key, "").strip() else " "
                        style = GREEN if filled == "✓" else DIM
                        console.print(f"  [{style}]{i + 1}. {filled} {s.label}[/]")
                    console.print()
                    try:
                        pick = int(Prompt.ask(f"  [{ACCENT}]Section number[/]")) - 1
                        if 0 <= pick < len(SECTIONS):
                            step = pick
                            break
                    except (ValueError, KeyboardInterrupt):
                        pass
                elif action == "quit":
                    console.print(f"  [{DIM}]Done.[/]")
                    return

            continue

        section = SECTIONS[step]
        guidance_map = get_guidance(task_type)
        guidance = guidance_map[section.key]

        show_step_bar(step, data)
        show_section_header(section, guidance, step)
        show_tips(guidance.tips)
        show_nav_help()

        existing = data.get(section.key, "").strip()
        if existing:
            console.print(f"  [{DIM}]current content:[/]")
            for line in existing.split("\n")[:5]:
                console.print(f"  [{MUTED}]│ {line}[/]")
            if existing.count("\n") > 4:
                console.print(f"  [{DIM}]│ ... ({existing.count(chr(10)) - 4} more lines)[/]")
            console.print()

        action = Prompt.ask(
            f"  [{ACCENT}]>[/{ACCENT}]",
            default="write",
            show_default=False,
        ).strip().lower()

        if action in ("n", "next"):
            if not data.get(section.key, "").strip():
                msg = "Write content first, or use (s)kip to move on."
                console.print(f"  [{ORANGE}]{msg}[/{ORANGE}]")
                console.print()
            else:
                step += 1
        elif action in ("b", "back"):
            step = max(0, step - 1)
        elif action in ("s", "skip"):
            step += 1
        elif action in ("p", "preview"):
            fmt = args.output
            show_output(data, task_type, fmt)
            console.print()
            Prompt.ask(f"  [{DIM}]Press Enter to continue[/{DIM}]", default="")
        elif action in ("q", "quit"):
            msg = "You have content — save before quitting?"
            if data and Confirm.ask(f"  [{ORANGE}]{msg}[/{ORANGE}]"):
                fmt = args.output
                ext = fmt if fmt != "markdown" else "md"
                filename = args.file or f"greenlit_{task_type}.{ext}"
                os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
                with open(filename, "w") as f:
                    f.write(FORMATTERS[fmt](data, task_type))
                console.print(f"  [{GREEN}]Saved to {filename}[/]")
            return
        elif action in ("e", "edit"):
            for i, s in enumerate(SECTIONS):
                filled = "✓" if data.get(s.key, "").strip() else " "
                style = GREEN if filled == "✓" else DIM
                console.print(f"  [{style}]{i + 1}. {filled} {s.label}[/]")
            console.print()
            try:
                pick = int(Prompt.ask(f"  [{ACCENT}]Section number[/]")) - 1
                if 0 <= pick < len(SECTIONS):
                    step = pick
                else:
                    err = f"Invalid section number — enter 1-{len(SECTIONS)}."
                    console.print(f"  [{ORANGE}]{err}[/{ORANGE}]")
                    console.print()
            except (ValueError, KeyboardInterrupt):
                err = f"Invalid section number — enter 1-{len(SECTIONS)}."
                console.print(f"  [{ORANGE}]{err}[/{ORANGE}]")
                console.print()
        else:
            content = read_multiline(guidance.placeholder, section.default)
            if content:
                data[section.key] = content
                console.print(f"  [{GREEN}]✓ {section.label} saved[/{GREEN}]")
            else:
                console.print(f"  [{DIM}]Empty — skipping[/{DIM}]")
            console.print()
            step += 1


def main():
    parser = argparse.ArgumentParser(
        description="Structure prompts before you burn tokens.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--type", "-t",
        choices=list(TASK_TYPES.keys()),
        help="Task type (skip selection screen)",
    )
    parser.add_argument(
        "--output", "-o",
        choices=["xml", "markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--file", "-f",
        help="Output filename (default: greenlit_<type>.<ext>)",
    )
    parser.add_argument(
        "--copy", "-c",
        action="store_true",
        help="Copy output to clipboard after saving",
    )
    parser.add_argument(
        "--template", "-T",
        metavar="PATH",
        help="Path to a YAML template file for a custom task type",
    )

    args = parser.parse_args()

    cwd = os.path.realpath(os.getcwd())
    templates_dir = os.path.realpath(os.path.expanduser("~/.greenlit/templates"))

    if args.file:
        target = os.path.realpath(os.path.abspath(args.file))
        if not target.startswith(cwd + os.sep) and target != cwd:
            console.print("  [red]Error: --file path must be within the current directory.[/]")
            sys.exit(1)

    if args.template:
        target = os.path.realpath(os.path.abspath(args.template))
        in_cwd = target.startswith(cwd + os.sep) or target == cwd
        in_templates_dir = target.startswith(templates_dir + os.sep) or target == templates_dir
        if not in_cwd and not in_templates_dir:
            console.print(
                "  [red]Error: --template path must be within the current directory "
                f"or {templates_dir}[/]"
            )
            sys.exit(1)

    task_types = dict(TASK_TYPES)

    if args.template:
        try:
            from greenlit.guidance import register_guidance
            from greenlit.templates import load_template
            name, meta, _ = load_template(args.template)
            register_guidance(name, meta.pop("_guidance"))
            task_types[name] = meta
            # Auto-select the custom type if --type not given
            if not args.type:
                args.type = name
        except ImportError as exc:
            console.print(f"  [red]{exc}[/]")
            sys.exit(1)
        except (FileNotFoundError, ValueError) as exc:
            console.print(f"  [red]Template error: {exc}[/]")
            sys.exit(1)

    try:
        run(args, task_types=task_types)
    except KeyboardInterrupt:
        console.print(f"\n  [{DIM}]Interrupted.[/{DIM}]")
        sys.exit(0)
