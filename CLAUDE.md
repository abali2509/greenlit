# CLAUDE.md

`greenlit` is a CLI that builds structured task specs in nine sections (ASK, GOAL, CONTEXT, SCOPE, INPUTS, OUTPUTS, CONSTRAINT, ATTENTION, DONE) across six task types, then saves them as XML or Markdown files for agent consumption. The loop is: agent drafts, human reviews, agent verifies against DONE.

## Module layout

- `sections.py` — `Section`, `SectionGuidance` dataclasses; `SECTIONS` list; `TASK_TYPES` registry
- `guidance/` — one module per task type; each exports `GUIDANCE: dict[str, SectionGuidance]`; `__init__.py` exposes `get_guidance(task_type)` and `get_default_constraints(task_type)`
- `formatters.py` — `format_xml`, `format_markdown`, `FORMATTERS` dict, `format_prompt()` dispatcher (pure functions)
- `parser.py` — inverse of `formatters.py`: parses XML/Markdown specs back into `(task_type, data)`; round-trip guaranteed
- `draft_meta.py` — pure string builder for the `greenlit draft` meta-prompt (no API calls)
- `display.py` — all `rich` rendering: step bar, section header, tips, output, nav help, editor integration
- `cli.py` — `argparse` setup, path-traversal guards, `run()` main loop; subcommands `draft`, `review`, `list`, `show`, `new`, `init`
- `init_cmd.py` — `greenlit init`: installs bundled skill files to user or project destinations
- `skills/skill.md` — the greenlit-Read agent skill (product surface; ships in the wheel)
- `skills/skill_write.md` — the greenlit-Write agent skill (product surface; ships in the wheel)
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
5. `DONE` is mandatory in emitted specs — it holds the testable acceptance criteria the executing agent is held to.
