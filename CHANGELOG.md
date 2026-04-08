# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- `--version` / `-V` flag to CLI
- Test coverage measurement with `pytest-cov` in CI and dev deps
- `greenlit init` subcommand to install agent skill into `.claude/skills/` or `.github/`
- Namespaced prompt output: `<dir>/<name>/<type>.<ext>` with collision suffix
- Vim/nvim editor integration for section content entry (`--no-editor` for inline fallback)
- Single-char task type aliases in interactive selector (r, p, a, d, rs)
- YAML custom template support via `-T` flag
- CI pipeline: tests (3.11/3.12/3.13), lint, wheel smoke test
- PyPI release workflow with Trusted Publishing (TestPyPI)
- Branch protection and rulesets on `main`
- CI, Release, and Ruff badges in README

### Fixed
- Clipboard fallback chain on Linux: `xclip` → `xsel` → `wl-copy`
- `show_transition()` no longer clears terminal scrollback history
- readline ANSI prompt corruption (patched `Console.input`, wrapped escapes in non-printing markers)
- Path traversal guards use `Path.is_relative_to` instead of string `startswith`
- README JSON output example now reflects actual nested `"sections"` structure

### Changed
- PyPI metadata added to `pyproject.toml` (readme, license, authors, keywords, classifiers)

## [0.1.0] - 2026-04-05

Initial release.

- Nine-section structured prompt walkthrough (ASK, GOAL, CONTEXT, SCOPE, DELEGATION, INPUTS, OUTPUTS, CONSTRAINT, ATTENTION)
- Five built-in task types: review, plan, action, debug, research
- Three output formats: XML, Markdown, JSON
- Interactive navigation: next, back, skip, preview, edit, quit
- Rich terminal UI with step progress bar and section guidance
