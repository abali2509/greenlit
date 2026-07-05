"""CLI entry point: argparse, main loop."""

import argparse
import datetime
import os
import platform
import subprocess
import sys
from pathlib import Path

from rich.prompt import Confirm, Prompt
from rich.table import Table

import greenlit.display as _display
from greenlit.display import (
    ACCENT,
    DIM,
    GREEN,
    MUTED,
    ORANGE,
    console,
    open_editor,
    read_multiline,
    show_header,
    show_nav_help,
    show_output,
    show_section_header,
    show_step_bar,
    show_task_selector,
    show_tips,
    show_transition,
)
from greenlit.formatters import FORMATTERS
from greenlit.guidance import get_default_constraints, get_guidance
from greenlit.sections import SECTIONS, TASK_TYPES


def _copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard. Returns True on success."""
    system = platform.system()
    if system == "Darwin":
        candidates = [["pbcopy"]]
    elif system == "Windows":
        candidates = [["clip.exe"]]
    else:
        candidates = [
            ["xclip", "-selection", "clipboard"],
            ["xsel", "--clipboard", "--input"],
            ["wl-copy"],
        ]
    for cmd in candidates:
        try:
            proc = subprocess.run(cmd, input=text.encode(), capture_output=True)
            if proc.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.SubprocessError):
            continue
    return False


def _resolve_output_path(root_dir: str, name: str, task_type: str, fmt: str) -> str:
    """Return <root_dir>/<name>/<task_type>.<ext>, appending _2, _3 … on collision."""
    ext = fmt if fmt != "markdown" else "md"
    base = os.path.join(root_dir, name, f"{task_type}.{ext}")
    if not os.path.exists(base):
        return base
    counter = 2
    while True:
        candidate = os.path.join(root_dir, name, f"{task_type}_{counter}.{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def _provision_output_dir(
    out_path: str, root_dir: str, cwd: str, private: bool = False
) -> None:
    """Create the output directory; add .greenlit/ to .gitignore only when --private."""
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    if not private:
        return
    default_root = os.path.realpath(os.path.join(cwd, ".greenlit"))
    if os.path.realpath(root_dir) == default_root:
        gitignore = os.path.join(cwd, ".gitignore")
        if os.path.exists(gitignore):
            with open(gitignore) as f:
                existing = f.read()
            if ".greenlit/" not in existing and ".greenlit\n" not in existing:
                with open(gitignore, "a") as f:
                    f.write("\n.greenlit/\n")


def run_list(args) -> None:
    """Walk .greenlit/ and print a table of saved prompts."""
    root = Path(args.dir)
    if not root.is_dir():
        console.print(f"  [{DIM}]No prompts found — {root}/ does not exist.[/]")
        return

    entries = []
    for prompt_dir in sorted(root.iterdir()):
        if not prompt_dir.is_dir():
            continue
        for f in sorted(prompt_dir.iterdir()):
            if f.suffix not in (".xml", ".md"):
                continue
            fmt = "xml" if f.suffix == ".xml" else "markdown"
            mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime)
            entries.append((prompt_dir.name, f.stem, fmt, mtime.strftime("%Y-%m-%d %H:%M")))

    if not entries:
        console.print(f"  [{DIM}]No prompts found in {root}/[/]")
        return

    table = Table(show_header=True, box=None, pad_edge=False, show_edge=False)
    table.add_column("name", style=GREEN)
    table.add_column("type", style=ACCENT)
    table.add_column("format", style=DIM)
    table.add_column("modified", style=DIM)
    for name, stem, fmt, mtime in entries:
        table.add_row(name, stem, fmt, mtime)
    console.print()
    console.print(table)
    console.print()


def run_show(args) -> None:
    """Print a prompt file to stdout."""
    path = Path(args.path)
    if not path.exists():
        console.print(f"  [red]File not found: {path}[/]")
        sys.exit(1)
    sys.stdout.write(path.read_text())


def run_review(args) -> None:
    """Load a drafted greenlit file and step through it as a review."""
    from greenlit.parser import parse_file

    path = Path(args.file)
    if not path.exists():
        console.print(f"  [red]File not found: {path}[/]")
        sys.exit(1)

    try:
        task_type, data = parse_file(str(path))
    except (ValueError, OSError) as exc:
        console.print(f"  [red]Could not parse {path}: {exc}[/]")
        sys.exit(1)

    if task_type not in TASK_TYPES:
        console.print(f"  [red]Unknown task type {task_type!r} in {path}.[/]")
        sys.exit(1)

    # Save back to the same file and format by default.
    args.type = task_type
    args.name = path.parent.name or task_type
    args.output = "xml" if path.suffix == ".xml" else "markdown"
    args.file = str(path)

    run(args, prefilled=data, task_type_override=task_type, review=True)


def run_draft(args) -> None:
    """Emit a meta-prompt instructing an agent to author a greenlit spec."""
    from rich.console import Console

    from greenlit.draft_meta import build_meta_prompt

    meta = build_meta_prompt(args.ask, args.type)
    sys.stdout.write(meta)
    if not meta.endswith("\n"):
        sys.stdout.write("\n")

    if getattr(args, "copy", False):
        # Copy confirmation is chrome — keep stdout clean for piping.
        err = Console(stderr=True)
        if _copy_to_clipboard(meta):
            err.print(f"  [{GREEN}]Copied to clipboard[/]")
        else:
            err.print(f"  [{ORANGE}]Warning: no clipboard tool found[/]")


def run_new(args) -> None:
    """Non-interactive prompt creation from --set key=value pairs."""
    valid_keys = {s.key for s in SECTIONS}
    data: dict[str, str] = {}
    stdin_used = False

    for kv in (args.set or []):
        if "=" not in kv:
            console.print(f"  [red]--set requires key=value format, got {kv!r}[/]")
            sys.exit(1)
        key, _, val = kv.partition("=")
        if key not in valid_keys:
            console.print(
                f"  [red]Unknown section {key!r}. "
                f"Valid keys: {', '.join(sorted(valid_keys))}[/]"
            )
            sys.exit(1)
        if val == "-":
            if stdin_used:
                console.print("  [red]Only one --set key=- (stdin read) is allowed.[/]")
                sys.exit(1)
            val = sys.stdin.read()
            stdin_used = True
        data[key] = val

    # Seed default constraints unless the user set CONSTRAINT explicitly or opted out.
    if "constraint" not in data and not getattr(args, "no_default_constraints", False):
        defaults = get_default_constraints(args.type)
        if defaults:
            data["constraint"] = "\n".join(defaults)

    output = FORMATTERS[args.output](data, args.type)

    if getattr(args, "stdout", False):
        sys.stdout.write(output)
        if not output.endswith("\n"):
            sys.stdout.write("\n")
        return

    if args.file:
        filename = args.file
        os.makedirs(os.path.dirname(os.path.abspath(filename)) or ".", exist_ok=True)
    else:
        root_dir = args.dir
        prompt_name = args.name or args.type
        filename = _resolve_output_path(root_dir, prompt_name, args.type, args.output)
        _provision_output_dir(
            filename, root_dir, os.getcwd(), private=getattr(args, "private", False)
        )

    with open(filename, "w") as f:
        f.write(output)
    console.print(f"  [{GREEN}]Saved to {filename}[/]")


def _save_prompt(
    data: dict[str, str],
    task_type: str,
    fmt: str,
    args,
    prompt_name: str,
) -> str:
    """Write formatted prompt to disk, handle clipboard copy. Returns saved filename."""
    output = FORMATTERS[fmt](data, task_type)
    if args.file:
        filename = args.file
    else:
        root_dir = getattr(args, "dir", ".greenlit")
        filename = _resolve_output_path(root_dir, prompt_name, task_type, fmt)
        _provision_output_dir(
            filename, root_dir, os.getcwd(), private=getattr(args, "private", False)
        )
    with open(filename, "w") as f:
        f.write(output)
    console.print(f"  [{GREEN}]Saved to {filename}[/]")
    if getattr(args, "copy", False):
        if _copy_to_clipboard(output):
            console.print(f"  [{GREEN}]Copied to clipboard[/]")
        else:
            msg = "Warning: no clipboard tool found (pbcopy/xclip/clip.exe)"
            console.print(f"  [{ORANGE}]{msg}[/]")
    return filename


def _pick_section(data: dict[str, str], sections: list) -> int | None:
    """Print section list and ask the user to pick one. Returns 0-based index or None."""
    for i, s in enumerate(sections):
        filled = "✓" if data.get(s.key, "").strip() else " "
        style = GREEN if filled == "✓" else DIM
        console.print(f"  [{style}]{i + 1}. {filled} {s.label}[/]")
    console.print()
    try:
        pick = int(Prompt.ask(f"  [{ACCENT}]Section number[/]")) - 1
        if 0 <= pick < len(sections):
            return pick
        err = f"Invalid section number — enter 1-{len(sections)}."
        console.print(f"  [{ORANGE}]{err}[/{ORANGE}]")
        console.print()
    except (ValueError, KeyboardInterrupt):
        err = f"Invalid section number — enter 1-{len(sections)}."
        console.print(f"  [{ORANGE}]{err}[/{ORANGE}]")
        console.print()
    return None


def run(
    args,
    task_types: dict | None = None,
    prefilled: dict | None = None,
    task_type_override: str | None = None,
    review: bool = False,
):
    if task_types is None:
        task_types = TASK_TYPES

    show_header()

    # Task type selection
    if task_type_override:
        task_type = task_type_override
        label = task_types[task_type]["label"]
        verb = "Reviewing" if review else "Task type:"
        console.print(f"  [{GREEN}]{verb}[/] {label}")
        console.print()
    elif args.type and args.type in task_types:
        task_type = args.type
        console.print(f"  [{GREEN}]Task type:[/] {task_types[task_type]['label']}")
        console.print()
    else:
        task_type = show_task_selector(task_types)

    prompt_name = getattr(args, "name", None) or ""
    if not prompt_name:
        prompt_name = Prompt.ask(
            f"  [{ACCENT}]Prompt name[/{ACCENT}]",
            default=task_type,
        )
    console.print()

    from rich.rule import Rule
    mode = "review" if review else "walkthrough"
    console.print(
        Rule(
            f" {task_types[task_type]['label']} {mode} ",
            style=ACCENT,
        )
    )
    console.print()

    guidance_map = get_guidance(task_type)
    if getattr(args, "lite", False):
        lite_keys = {"ask", "scope", "done"}
        sections = [s for s in SECTIONS if s.key in lite_keys]
    else:
        sections = SECTIONS
    data: dict[str, str] = dict(prefilled) if prefilled else {}

    # Seed the CONSTRAINT section with the task type's default constraints as
    # editable starting content. Never in review mode (the file is the contract).
    prefilled_default_keys: set[str] = set()
    if not review and "constraint" not in data:
        defaults = get_default_constraints(task_type)
        if defaults:
            data["constraint"] = "\n".join(defaults)
            prefilled_default_keys.add("constraint")

    step = 0

    while True:
        if step >= len(sections):
            fmt = args.output
            if getattr(args, "stdout", False):
                output = FORMATTERS[fmt](data, task_type)
                sys.stdout.write(output)
                if not output.endswith("\n"):
                    sys.stdout.write("\n")
                return
            show_output(data, task_type, fmt)
            console.print()

            while True:
                action = Prompt.ask(
                    f"  [{ACCENT}]Action[/{ACCENT}]",
                    choices=["xml", "markdown", "save", "edit", "quit"],
                    default="save",
                    show_choices=True,
                )

                if action in FORMATTERS:
                    fmt = action
                    show_output(data, task_type, fmt)
                    console.print()
                elif action == "save":
                    _save_prompt(data, task_type, fmt, args, prompt_name)
                    console.print()
                    return
                elif action == "edit":
                    pick = _pick_section(data, sections)
                    if pick is not None:
                        step = pick
                        break
                elif action == "quit":
                    console.print(f"  [{DIM}]Done.[/]")
                    return

            continue

        section = sections[step]
        guidance = guidance_map[section.key]

        show_step_bar(step, data, sections)
        show_section_header(section, guidance, step, len(sections))
        show_tips(guidance.tips, review=review)
        show_nav_help()

        existing = data.get(section.key, "").strip()
        if existing:
            if section.key in prefilled_default_keys:
                console.print(
                    f"  [{DIM}]pre-filled default — edit, keep, or clear all as needed:[/]"
                )
            else:
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
                show_transition()
                step += 1
        elif action in ("b", "back"):
            show_transition()
            step = max(0, step - 1)
        elif action in ("s", "skip"):
            show_transition()
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
                _save_prompt(data, task_type, fmt, args, prompt_name)
            return
        elif action in ("e", "edit"):
            pick = _pick_section(data, sections)
            if pick is not None:
                step = pick
        else:
            current = data.get(section.key, "") or section.default
            if getattr(args, "no_editor", False):
                content = read_multiline(
                    guidance.placeholder,
                    current,
                    hint=guidance.hint,
                    tips=guidance.tips,
                )
            else:
                content = open_editor(
                    guidance.placeholder,
                    current,
                    hint=guidance.hint,
                    tips=guidance.tips,
                )
            if content:
                data[section.key] = content
                console.print(f"  [{GREEN}]✓ {section.label} saved[/{GREEN}]")
            else:
                # Cleared — drop any prior content (including a pre-filled default).
                data.pop(section.key, None)
                console.print(f"  [{DIM}]Empty — skipping[/{DIM}]")
            prefilled_default_keys.discard(section.key)
            console.print()
            step += 1


def main():
    from greenlit import __version__

    parser = argparse.ArgumentParser(
        description="Structure prompts before you burn tokens.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")

    # ── init subcommand ───────────────────────────────────────────────
    subparsers.add_parser(
        "init",
        help=(
            "Install the greenlit-Read agent skill: "
            "user-global ~/.claude/skills/, "
            "project .claude/skills/, "
            "or repo .github/instructions/"
        ),
    )

    # ── draft subcommand ──────────────────────────────────────────────
    draft_p = subparsers.add_parser(
        "draft",
        help="Emit a meta-prompt telling an agent to author a greenlit spec",
    )
    draft_p.add_argument("ask", help="One-line description of the task")
    draft_p.add_argument(
        "--type", "-t",
        choices=list(TASK_TYPES.keys()),
        help="Task type (agent infers if omitted)",
    )
    draft_p.add_argument(
        "--copy", "-c",
        action="store_true",
        help="Copy the meta-prompt to clipboard",
    )

    # ── review subcommand ─────────────────────────────────────────────
    review_p = subparsers.add_parser(
        "review",
        help="Step through an existing greenlit file, reviewing each section",
    )
    review_p.add_argument("file", help="Path to a greenlit .xml or .md file")
    review_p.add_argument(
        "--copy", "-c",
        action="store_true",
        help="Copy output to clipboard after saving",
    )
    review_p.add_argument(
        "--no-editor",
        action="store_true",
        help="Use inline input instead of opening vim/nvim",
    )

    # ── list subcommand ───────────────────────────────────────────────
    list_p = subparsers.add_parser("list", help="List saved prompts in .greenlit/")
    list_p.add_argument(
        "--dir", "-d",
        default=".greenlit",
        help="Root directory to list (default: .greenlit/)",
    )

    # ── show subcommand ───────────────────────────────────────────────
    show_p = subparsers.add_parser("show", help="Print a saved prompt file to stdout")
    show_p.add_argument("path", help="Path to the prompt file")

    # ── new subcommand ────────────────────────────────────────────────
    new_p = subparsers.add_parser(
        "new",
        help="Create a prompt non-interactively from --set key=value pairs",
    )
    new_p.add_argument(
        "--type", "-t",
        choices=list(TASK_TYPES.keys()),
        required=True,
        help="Task type",
    )
    new_p.add_argument(
        "--set", "-s",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Set a section value (use KEY=- to read from stdin)",
    )
    new_p.add_argument(
        "--output", "-o",
        choices=["xml", "markdown"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    new_p.add_argument(
        "--file", "-f",
        help="Full output path (overrides --dir / --name)",
    )
    new_p.add_argument(
        "--dir", "-d",
        default=".greenlit",
        help="Root output directory (default: .greenlit/)",
    )
    new_p.add_argument(
        "--name", "-n",
        help="Prompt namespace slug (default: task type)",
    )
    new_p.add_argument(
        "--stdout",
        action="store_true",
        help="Print to stdout instead of saving; UI chrome goes to stderr",
    )
    new_p.add_argument(
        "--private",
        action="store_true",
        help="Add .greenlit/ to .gitignore (default: leave .gitignore untouched)",
    )
    new_p.add_argument(
        "--no-default-constraints",
        action="store_true",
        help="Omit the task type's default CONSTRAINT lines",
    )

    # ── run (default walkthrough) — flags on the root parser ─────────
    parser.add_argument(
        "--type", "-t",
        choices=list(TASK_TYPES.keys()),
        help="Task type (skip selection screen)",
    )
    parser.add_argument(
        "--output", "-o",
        choices=["xml", "markdown"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--file", "-f",
        help="Full output path (overrides --dir / --name)",
    )
    parser.add_argument(
        "--dir", "-d",
        default=".greenlit",
        help="Root output directory (default: .greenlit/)",
    )
    parser.add_argument(
        "--name", "-n",
        help="Prompt namespace slug, e.g. auth-refactor (prompted if omitted)",
    )
    parser.add_argument(
        "--copy", "-c",
        action="store_true",
        help="Copy output to clipboard after saving",
    )
    parser.add_argument(
        "--no-editor",
        action="store_true",
        help="Use inline input instead of opening vim/nvim",
    )
    parser.add_argument(
        "--lite",
        action="store_true",
        help="Three-section walkthrough: ASK, SCOPE, DONE",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print to stdout instead of saving; UI chrome goes to stderr",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Add .greenlit/ to .gitignore (default: leave .gitignore untouched)",
    )

    args = parser.parse_args()

    # ── stdout mode: redirect UI chrome to stderr ─────────────────────
    if getattr(args, "stdout", False):
        global console  # noqa: PLW0603
        _display.use_stderr()
        console = _display.console

    # ── dispatch init ─────────────────────────────────────────────────
    if args.command == "review":
        try:
            run_review(args)
        except KeyboardInterrupt:
            console.print(f"\n  [{DIM}]Interrupted.[/{DIM}]")
        return

    if args.command == "draft":
        run_draft(args)
        return

    if args.command == "list":
        run_list(args)
        return

    if args.command == "show":
        run_show(args)
        return

    if args.command == "new":
        cwd = Path(os.path.realpath(os.getcwd()))
        if args.file:
            target = Path(os.path.realpath(os.path.abspath(args.file)))
            if not (target == cwd or target.is_relative_to(cwd)):
                console.print("  [red]Error: --file path must be within the current directory.[/]")
                sys.exit(1)
        if args.dir:
            target = Path(os.path.realpath(os.path.abspath(args.dir)))
            if not (target == cwd or target.is_relative_to(cwd)):
                console.print("  [red]Error: --dir path must be within the current directory.[/]")
                sys.exit(1)
        try:
            run_new(args)
        except KeyboardInterrupt:
            console.print(f"\n  [{DIM}]Interrupted.[/{DIM}]")
        return

    if args.command == "init":
        from greenlit.init_cmd import run_init
        try:
            run_init()
        except KeyboardInterrupt:
            console.print(f"\n  [{DIM}]Interrupted.[/{DIM}]")
        return

    # ── walkthrough ───────────────────────────────────────────────────
    cwd = Path(os.path.realpath(os.getcwd()))

    if args.file:
        target = Path(os.path.realpath(os.path.abspath(args.file)))
        if not (target == cwd or target.is_relative_to(cwd)):
            console.print("  [red]Error: --file path must be within the current directory.[/]")
            sys.exit(1)

    if args.dir:
        target = Path(os.path.realpath(os.path.abspath(args.dir)))
        if not (target == cwd or target.is_relative_to(cwd)):
            console.print("  [red]Error: --dir path must be within the current directory.[/]")
            sys.exit(1)

    try:
        run(args)
    except KeyboardInterrupt:
        console.print(f"\n  [{DIM}]Interrupted.[/{DIM}]")
        sys.exit(0)
