# CLAUDE.md

`greenlit` is a CLI that walks users through building structured task prompts in eight sections (ASK, GOAL, CONTEXT, SCOPE, INPUTS, OUTPUTS, CONSTRAINT, ATTENTION) across five task types, then saves them as XML or Markdown files for agent consumption.

## Module layout

- `sections.py` — `Section`, `SectionGuidance` dataclasses; `SECTIONS` list; `TASK_TYPES` registry
- `guidance/` — one module per task type; each exports `GUIDANCE: dict[str, SectionGuidance]`; `__init__.py` exposes `get_guidance(task_type)`
- `formatters.py` — `format_xml`, `format_markdown`, `FORMATTERS` dict, `format_prompt()` dispatcher (pure functions)
- `display.py` — all `rich` rendering: step bar, section header, tips, output, nav help, editor integration
- `cli.py` — `argparse` setup, path-traversal guards, `run()` main loop
- `init_cmd.py` — `greenlit init`: installs bundled skill file to user or project destinations
- `skills/skill.md` — the greenlit-Read agent skill (product surface; ships in the wheel)
- `__main__.py` — calls `cli.main()` so `python -m greenlit` works

## Verification loop

After every change run both of these; both must pass before committing:

```
pytest
ruff check src/ tests/
```

## Hard rules

1. `rich` is the only runtime dependency — never add another.
2. Formatters are pure functions — no side effects, no I/O.
3. `skills/*.md` are product surface — any format change must update them in the same commit.
4. Commit messages are one-line Conventional Commits (`type(scope): description`).

## Active refactor

Governed by `greenlit-v0.2-refactor-plan.md` — read it before making changes.
