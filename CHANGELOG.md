# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-07-05

Repositions greenlit from a prompt-walkthrough CLI to a lightweight spec layer: the agent drafts, the human reviews, the agent verifies against DONE. **No compatibility shims** — pre-1.0 and previously unpublished, greenlit files from 0.1.0 are simply invalid under the new format.

### Added
- DONE section — testable acceptance criteria (EARS-style, runnable checks), positioned last. The greenlit-Read skill now executes every DONE item and reports pass/fail before declaring completion.
- `greenlit draft "<ask>"` — emits an agent-authoring meta-prompt (stdout, optional `--copy`) that tells an agent to interview the user and produce a greenlit spec. Offline, no dependencies.
- `greenlit review <file>` — loads an existing greenlit file (XML or Markdown) and steps through it with content pre-filled, reframing guidance as review checklists.
- `greenlit new -t <type> --set key=value ...` — non-interactive prompt creation; `key=-` reads from stdin; `--stdout` prints instead of saving.
- `greenlit list` / `greenlit show <path>` — tabulate the `.greenlit/` library and print a saved spec to stdout.
- `--lite` flag — three-section walkthrough (ASK, SCOPE, DONE) for medium-sized tasks.
- `--stdout` flag for `new` and the walkthrough: formatted spec to stdout, all UI chrome to stderr (pipeline-safe).
- `--private` flag: opt in to writing `.greenlit/` to `.gitignore`.
- Second bundled skill `greenlit-Write` — teaches an agent to author greenlit specs. `greenlit init` now installs both skills per target, and offers project-level Claude Code (`.claude/skills/`) alongside user-global Claude and repo-level Copilot.
- `parser.py` — XML/Markdown prompt parser with round-trip guarantees against the formatters.
- Format version stamp: XML gets a `greenlit="0.2"` attribute; Markdown gets a `<!-- greenlit: 0.2 -->` comment.

### Changed
- `.greenlit/` is now version-controlled by default — the `.gitignore` auto-append was removed (opt back in with `--private`). Specs are intent worth committing.
- Repositioned package description and README around the draft → review → execute → verify loop; README leads with `uvx greenlit`.
- Release workflow now publishes to real PyPI via Trusted Publishing on `v*` tags.
- `greenlit init` (0.1 fixes): Copilot instructions now install to repo-level `.github/instructions/` (was a dead `~/.github/` path); `importlib.resources.read_text` replaced with `files().joinpath().read_text()`.

### Removed
- DELEGATION section — from the format, all task-type guidance, and the skill. Orchestrators self-decompose; it added ceremony without value.
- JSON output format — XML and Markdown are the two canonical formats; JSON was semantically identical to XML with no distinct consumers.
- YAML custom template system (`templates.py`, `--template/-T`, the `pyyaml` optional dependency, `register_guidance`) — fought the tool's simplicity value. **`rich` is now the only dependency, with zero extras.**

### Fixed
- `_copy_to_clipboard` now actually executes the command on macOS (`pbcopy`) and Windows (`clip.exe`); previously only the Linux fallback chain ran.

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
