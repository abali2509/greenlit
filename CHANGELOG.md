# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- DONE section — testable acceptance criteria (EARS-style, runnable checks), positioned last. The greenlit-Read skill now executes every DONE item and reports pass/fail before declaring completion.
- `--lite` flag — three-section walkthrough (ASK, SCOPE, DONE) for medium-sized tasks.
- `greenlit draft "<ask>"` — emits an agent-authoring meta-prompt (stdout, optional `--copy`) that tells an agent to interview the user and produce a greenlit spec. Offline, no dependencies.
- `greenlit review <file>` — loads an existing greenlit file (XML or Markdown) and steps through it with content pre-filled, reframing guidance as review checklists.
- `parser.py` — XML/Markdown prompt parser with round-trip guarantees against the formatters.
- Second bundled skill `greenlit-Write` — teaches an agent to author greenlit specs. `greenlit init` now installs both skills per target.
- `greenlit new -t <type> --set key=value ...` — non-interactive prompt creation; `key=-` reads from stdin; `--stdout` prints instead of saving.
- `--stdout` flag for both `new` and the interactive walkthrough: formatted prompt goes to stdout, all UI chrome to stderr (pipeline-safe).
- `--private` flag: opt in to writing `.greenlit/` to `.gitignore` (default is now to leave `.gitignore` untouched, version-controlling specs).
- `greenlit list` — tabulates saved prompts in `.greenlit/` (name, type, format, modified).
- `greenlit show <path>` — prints a saved prompt file to stdout.
- Format version stamp: XML gets `greenlit="0.2"` attribute; Markdown gets `<!-- greenlit: 0.2 -->` comment.

### Removed
- DELEGATION section removed from the prompt format, all task-type guidance, and the greenlit-Read skill. Orchestrators self-decompose; DELEGATION added ceremony without value.
- JSON output format removed. XML and Markdown are the two canonically supported formats; JSON was semantically identical to XML with no distinct consumers.
- YAML custom template system removed (`templates.py`, `--template/-T` flag, `pyyaml` optional dependency, `register_guidance`). Feature fought the tool's simplicity value and required an optional dependency.

### Fixed
- `_copy_to_clipboard` now actually executes the command on macOS (`pbcopy`) and Windows (`clip.exe`); previously only the Linux fallback chain ran.
- `greenlit init` option 2 now writes Copilot instructions to `<repo>/.github/instructions/greenlit.instructions.md` (repo-level, where Copilot reads it) instead of `~/.github/` (home directory, dead path).

### Added
- `greenlit init` option 3: install skill to `<cwd>/.claude/skills/greenlit-Read/SKILL.md` for project-level Claude Code.

### Changed
- `importlib.resources.read_text` replaced with `files().joinpath().read_text()` — eliminates deprecation warning.
- `cli.py` internal: extracted `_save_prompt` and `_pick_section` helpers; `get_guidance` hoisted out of the section loop.

## [0.1.0] - 2026-04-08

### Added
- Nine-section structured prompt walkthrough (ASK, GOAL, CONTEXT, SCOPE, DELEGATION, INPUTS, OUTPUTS, CONSTRAINT, ATTENTION)
- Five built-in task types: review, plan, action, debug, research
- Three output formats: XML, Markdown, JSON
- Interactive navigation: next, back, skip, preview, edit, quit
- Rich terminal UI with step progress bar and section guidance
- `--version` / `-V` flag to CLI
- `greenlit init` subcommand to install agent skill into `~/.claude/skills/` or `~/.github/`
- Namespaced prompt output: `<dir>/<name>/<type>.<ext>` with collision suffix
- Vim/nvim editor integration for section content entry (`--no-editor` for inline fallback)
- Single-char task type aliases in interactive selector (r, p, a, d, rs)
- YAML custom template support via `-T` flag
- Test coverage measurement with `pytest-cov` in CI and dev deps
- CI pipeline: tests (3.11/3.12/3.13), lint, wheel smoke test
- PyPI release workflow with Trusted Publishing (TestPyPI)
- CI, Release, and Ruff badges in README

### Fixed
- Clipboard fallback chain on Linux: `xclip` → `xsel` → `wl-copy`
- `show_transition()` no longer clears terminal scrollback history
- readline ANSI prompt corruption (patched `Console.input`, wrapped escapes in non-printing markers)
- Path traversal guards use `Path.is_relative_to` instead of string `startswith`
