"""greenlit init — install the bundled skill template into ~/.claude/skills/ or ~/.github/."""

import importlib.resources
import os

from rich.prompt import Prompt

from greenlit.display import ACCENT, DIM, GREEN, console

_HOME = os.path.expanduser("~")


def _get_targets() -> dict[str, tuple[str, str]]:
    return {
        "1": (os.path.join(_HOME, ".claude", "skills", "greenlit-Read"), "SKILL.md"),
        "2": (os.path.join(_HOME, ".github"), "read-greenlit-prompt.md"),
    }


def run_init() -> None:
    console.print()
    console.print(f"  [{ACCENT}]greenlit init[/] — install agent skill\n")
    console.print(f"  [{DIM}]Where should the skill be written?[/]")
    console.print(f"  [{DIM}]  1  ~/.claude/skills/  (Claude Code)[/]")
    console.print(f"  [{DIM}]  2  ~/.github/          (GitHub Copilot)[/]")
    console.print()

    choice = Prompt.ask(
        f"  [{ACCENT}]Choice[/{ACCENT}]",
        choices=["1", "2"],
        show_choices=False,
    )

    target_dir, filename = _get_targets()[choice]
    dest = os.path.join(target_dir, filename)

    skill_text = importlib.resources.read_text("greenlit.skills", "skill.md")

    os.makedirs(target_dir, exist_ok=True)
    with open(dest, "w") as f:
        f.write(skill_text)

    console.print(f"\n  [{GREEN}]Skill written to {dest}[/]")
    console.print(f"  [{DIM}]Invoke it with /greenlit-Read in your agent.[/]\n")
