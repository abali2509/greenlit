"""greenlit init — install bundled skill into user or project Claude/Copilot dirs."""

import importlib.resources
import os

from rich.prompt import Prompt

from greenlit.display import ACCENT, DIM, GREEN, console

_HOME = os.path.expanduser("~")


def _get_targets(cwd: str) -> dict[str, tuple[str, str]]:
    return {
        "1": (os.path.join(_HOME, ".claude", "skills", "greenlit-Read"), "SKILL.md"),
        "2": (os.path.join(cwd, ".claude", "skills", "greenlit-Read"), "SKILL.md"),
        "3": (os.path.join(cwd, ".github", "instructions"), "greenlit.instructions.md"),
    }


def run_init() -> None:
    cwd = os.getcwd()
    console.print()
    console.print(f"  [{ACCENT}]greenlit init[/] — install agent skill\n")
    console.print(f"  [{DIM}]Where should the skill be written?[/]")
    console.print(f"  [{DIM}]  1  ~/.claude/skills/greenlit-Read/  (Claude Code, user-global)[/]")
    console.print(f"  [{DIM}]  2  .claude/skills/greenlit-Read/    (Claude Code, project-level)[/]")
    console.print(f"  [{DIM}]  3  .github/instructions/            (GitHub Copilot, repo-level)[/]")
    console.print()

    choice = Prompt.ask(
        f"  [{ACCENT}]Choice[/{ACCENT}]",
        choices=["1", "2", "3"],
        show_choices=False,
    )

    target_dir, filename = _get_targets(cwd)[choice]
    dest = os.path.join(target_dir, filename)

    skill_text = importlib.resources.files("greenlit.skills").joinpath("skill.md").read_text()

    os.makedirs(target_dir, exist_ok=True)
    with open(dest, "w") as f:
        f.write(skill_text)

    console.print(f"\n  [{GREEN}]Skill written to {dest}[/]")
    console.print(f"  [{DIM}]Invoke it with /greenlit-Read in your agent.[/]\n")
