"""greenlit init — install both bundled skills into user or project Claude/Copilot dirs."""

import importlib.resources
import os

from rich.prompt import Prompt

from greenlit.display import ACCENT, DIM, GREEN, console

_HOME = os.path.expanduser("~")

# (source resource in greenlit.skills, Claude skill dir name, Copilot filename)
_SKILLS = [
    ("skill.md", "greenlit-Read", "greenlit-read.instructions.md"),
    ("skill_write.md", "greenlit-Write", "greenlit-write.instructions.md"),
]


def _get_installs(cwd: str, choice: str) -> list[tuple[str, str]]:
    """Return a list of (source_resource, destination_path) for the chosen target."""
    installs = []
    for source, claude_name, copilot_name in _SKILLS:
        if choice == "1":
            dest = os.path.join(_HOME, ".claude", "skills", claude_name, "SKILL.md")
        elif choice == "2":
            dest = os.path.join(cwd, ".claude", "skills", claude_name, "SKILL.md")
        else:  # choice == "3"
            dest = os.path.join(cwd, ".github", "instructions", copilot_name)
        installs.append((source, dest))
    return installs


def run_init() -> None:
    cwd = os.getcwd()
    console.print()
    console.print(f"  [{ACCENT}]greenlit init[/] — install agent skills\n")
    console.print(f"  [{DIM}]Where should the skills be written?[/]")
    console.print(f"  [{DIM}]  1  ~/.claude/skills/     (Claude Code, user-global)[/]")
    console.print(f"  [{DIM}]  2  .claude/skills/       (Claude Code, project-level)[/]")
    console.print(f"  [{DIM}]  3  .github/instructions/ (GitHub Copilot, repo-level)[/]")
    console.print()

    choice = Prompt.ask(
        f"  [{ACCENT}]Choice[/{ACCENT}]",
        choices=["1", "2", "3"],
        show_choices=False,
    )

    console.print()
    for source, dest in _get_installs(cwd, choice):
        skill_text = importlib.resources.files("greenlit.skills").joinpath(source).read_text()
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as f:
            f.write(skill_text)
        console.print(f"  [{GREEN}]Skill written to {dest}[/]")

    console.print(
        f"\n  [{DIM}]Invoke /greenlit-Read to execute a spec, "
        f"/greenlit-Write to author one.[/]\n"
    )
