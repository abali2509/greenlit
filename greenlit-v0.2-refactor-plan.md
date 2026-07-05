# greenlit v0.2.0 — Refactoring & Development Plan

**Purpose:** implementation plan for the changes agreed in review (July 2026). Written to be executed by an AI coding agent phase-by-phase, with human review between phases.
**Repo:** https://github.com/abali2509/greenlit (plan verified against source at commit head, 84 tests passing on Python 3.12)
**Guiding values:** simplicity, maintainability, ease of use. Strategic direction: invert authoring from *human-writes-agent-reads* to *agent-drafts-human-reviews*; make the greenlit file format programmable, pipeable, and version-controlled; close the loop with verification.

**Execution rules for the agent:**
- Work one phase at a time, in order. Stop for human review at the end of each phase.
- Run `pytest` and `ruff check src/ tests/` after every change. All tests green before moving on.
- Update `CHANGELOG.md` under an `[Unreleased]` heading as you go.
- Commit after each numbered change, one commit per change, using the exact message from the **Commit plan** section at the end of this document.
- Do not touch anything listed in **Out of scope**.

---

## Current state (verified facts)

- `src/greenlit/` — cli.py (399 lines: argparse + walkthrough loop), display.py (295: rich UI, editor integration, readline patch), sections.py (93: 9 sections, 5 task types), formatters.py (54: xml/markdown/json), templates.py (76: YAML custom task types, pyyaml extra), init_cmd.py (44: skill installer), guidance/ (5 task-type modules), skills/skill.md (66 lines: greenlit-Read agent skill).
- Tests: 84 across 6 files. CI: pytest matrix 3.11–3.13 + ruff + wheel smoke test. Release workflow targets TestPyPI only.
- Known bugs: `--copy` broken on macOS/Windows; Copilot init path writes to a location Copilot does not read; deprecated `importlib.resources.read_text` (warning visible in test output).

---

## Phase 0 — Bug fixes & hygiene (no behavior redesign)

Small, isolated wins to build confidence and clean the ground.

### 0.0 Update CLAUDE.md — repo root (do this first)
A CLAUDE.md exists locally but is currently gitignored. Update it before any other change so the agent executing this plan works with proper project context, and bring it under version control — a project harness file should travel with the repo (same philosophy as change 2.3). Steps:
- Remove the `CLAUDE.md` entry from `.gitignore` and track the file.
- Merge the following into the existing content, preserving anything already there that is still accurate; keep the result under 50 lines, router-style:
  - What greenlit is (one paragraph) and the module layout (one line per module).
  - Verification loop: run `pytest` and `ruff check src/ tests/` after every change; both must pass before committing.
  - Hard rules: rich is the only runtime dependency — never add another; formatters stay pure functions; `skills/*.md` are product surface — any format change must update them in the same commit; commit messages are one-line Conventional Commits.
  - Pointer: "Active refactor governed by `greenlit-v0.2-refactor-plan.md` — read it before making changes."
- Drop anything in the existing file that contradicts this plan (e.g. references to DELEGATION, JSON output, or YAML templates).
**Acceptance:** file tracked by git and under 50 lines; contains the test/lint loop and the four hard rules; no stale references to features this plan removes; no duplication of README content.

### 0.1 Fix `_copy_to_clipboard` on macOS/Windows — `src/greenlit/cli.py`
The Darwin branch assigns `cmd = ["pbcopy"]` and the Windows branch `cmd = ["clip.exe"]`, but neither executes it — only the Linux `else` branch contains the `subprocess.run` loop, so the function implicitly returns `None` on Mac/Windows.
**Approach:** restructure so all platforms flow through one candidate-command loop (Darwin → `[pbcopy]`; Windows → `[clip.exe]`; Linux → xclip/xsel/wl-copy chain). Single `subprocess.run` execution path, explicit `return False` at the end.
**Tests:** parametrized unit test mocking `platform.system()` and `subprocess.run` for all three platforms, asserting the command is actually executed and the boolean return is correct.
**Acceptance:** `--copy` verified executed (via mock) on darwin/windows/linux paths; no implicit `None` return.

### 0.2 Fix the Copilot install target — `src/greenlit/init_cmd.py`
Option 2 writes to `~/.github/read-greenlit-prompt.md` (home directory). GitHub Copilot reads repo-level `.github/copilot-instructions.md` / `.github/instructions/*.instructions.md`, not a home-level `.github/`. The current target is almost certainly dead.
**Approach:** replace option 2's destination with `<cwd>/.github/instructions/greenlit.instructions.md` (repo-level). Before implementing, verify the current Copilot custom-instructions paths against GitHub's docs and adjust the filename/frontmatter to match.
**Acceptance:** file lands inside the current repo where Copilot discovers it; help text matches actual destination.

### 0.3 Add project-level Claude Code install option — `src/greenlit/init_cmd.py`
Currently only `~/.claude/skills/` (user-global). Add a third option: `<cwd>/.claude/skills/greenlit-Read/SKILL.md` so teams can commit the skill with the repo.
**Acceptance:** `greenlit init` offers user-global Claude, project-level Claude, and repo-level Copilot; each writes to the stated path; init help string in cli.py updated to match reality.

### 0.4 Replace deprecated `importlib.resources.read_text` — `src/greenlit/init_cmd.py`
Use `importlib.resources.files("greenlit.skills").joinpath("skill.md").read_text()`.
**Acceptance:** deprecation warning gone from test output.

### 0.5 Deduplicate cli.py internals — `src/greenlit/cli.py`
Extract: (a) `_save_prompt(data, task_type, fmt, args, prompt_name) -> str` used by both the post-walkthrough `save` action and the quit-with-save path; (b) `_pick_section(data) -> int | None` used by both copies of the edit-section picker. Hoist `get_guidance(task_type)` out of the while loop.
**Acceptance:** no duplicated save/picker logic; behavior identical; tests green.

---

## Phase 1 — Cuts (shrink surface before building)

Rationale: DELEGATION is obsolete (orchestrators self-decompose in 2026); JSON is a third semantically-identical format nobody consumes; YAML templates are an optional-dependency power feature that fights the tool's simplicity value.

### 1.1 Remove the DELEGATION section
- `sections.py`: delete the delegation `Section`.
- `guidance/*.py` (all five): delete the `"delegation"` guidance entries.
- `skills/skill.md`: remove DELEGATION from section list and semantics entirely.
- Tests: update section-count assertions in `test_sections.py` and any walkthrough integration tests.

### 1.2 Remove the JSON formatter
- `formatters.py`: delete `format_json`; `FORMATTERS` = xml, markdown.
- `cli.py`: remove `json` from `--output` choices and the post-walkthrough action choices.
- `skills/skill.md`: remove JSON from the recognized formats.
- Tests: prune JSON cases from `test_formatters.py`.

### 1.3 Remove the YAML template system
- Delete `templates.py` and `tests/test_templates.py`.
- `cli.py`: remove `--template/-T` flag, the templates-dir path guard, and the template-loading block in `main()`.
- `guidance/__init__.py`: remove `register_guidance` if it exists solely for templates.
- `pyproject.toml`: remove the `templates` optional dependency; CI: remove `--extra templates` from the test command in `.github/workflows/ci.yml`.
- README: remove template documentation.

**Phase acceptance:** package has exactly one runtime dependency (rich), zero extras; eight sections; two formats; all tests green; line count meaningfully down.

---

## Phase 2 — Make the format programmable, pipeable, and versioned

### 2.1 Non-interactive creation: `greenlit new`
New subcommand: `greenlit new -t action --set ask="..." --set scope="..." [--set <key>=<value> ...] [-o xml|markdown] [--stdout | -f FILE | default .greenlit/ path]`. Formatters are already pure functions — this is a thin argparse layer over them. Unknown section keys → clear error listing valid keys. Also accept full section content from stdin when `--set <key>=-` is given (read remaining stdin into that key).
**Why:** currently the interactive TUI is the *only* producer of greenlit files; this makes the format writable by scripts, hooks, and other agents.
**Tests:** integration tests invoking `new` via `main()` with monkeypatched argv; golden-file comparison for xml and markdown output.

### 2.2 Stdout as first-class output
Add `--stdout` (walkthrough and `new`): print the formatted prompt to stdout and nothing else on stdout (all UI chrome goes to stderr when `--stdout` is set), enabling `greenlit new ... --stdout | claude -p`.
**Acceptance:** piping produces clean prompt text with no rich markup or UI noise.

### 2.3 Reverse the gitignore default
`_provision_output_dir` currently auto-appends `.greenlit/` to `.gitignore`. Invert: never touch `.gitignore` by default (specs are version-controlled intent — spec-anchored is the point); add `--private` flag to opt in to the old behavior.
**Tests:** update the existing gitignore test; add `--private` case.

### 2.4 Version-stamp the artifact
- XML: `<prompt type="review" greenlit="0.2">`; Markdown: HTML comment `<!-- greenlit: 0.2 -->` under the title.
- `skills/skill.md`: note the attribute and its meaning.

### 2.5 Library commands: `greenlit list` / `greenlit show <name>`
`list`: walk `.greenlit/`, print name, task type, format, modified time. `show`: print a named prompt file to stdout (respecting 2.2 cleanliness). Keep it minimal — no rerun/diff machinery yet.
**Phase acceptance:** a greenlit file can be created, listed, shown, and piped entirely non-interactively.

---

## Phase 3 — New capabilities (the strategic inversion)

### 3.1 DONE section (verification), wired into the skill
- `sections.py`: add `Section(key="done", label="DONE", tagline="Testable acceptance criteria. How the agent proves it's finished.")` — position it last, after ATTENTION.
- `guidance/*.py`: add `done` guidance per task type. Hints should push EARS-style criteria ("WHEN <condition>, the system SHALL <behavior>") and *runnable* checks where possible (test command, lint command, a checklist for research/review types).
- `skills/skill.md`: extend the execution protocol with a final step: "Before declaring completion, execute or evaluate every item in DONE. Report each item as pass/fail. If any item fails, continue working or explicitly surface the failure — never declare done with unexamined criteria."
**Why:** converts a greenlit prompt from an organized request into a self-verifying loop — the mechanism behind spec-driven development's first-pass-success gains.

### 3.2 Lite tier: `--lite`
Three-section walkthrough: ASK, SCOPE, DONE. Implement by filtering `SECTIONS` in `run()` (do not fork the section model). Post-walkthrough `edit` picker and step bar must respect the active section list.
**Why:** owns the middle ground between plan-mode vibing and heavyweight SDD; main defense against the "nine sections is ceremony" objection.

### 3.3 `greenlit draft "<one-line ask>"` — agent-first authoring
New subcommand that emits (stdout + optional `--copy`) a **meta-prompt** instructing an agent to: interview the user about gaps, then produce a valid greenlit XML file for task type `-t` (agent infers if omitted) covering all sections including DONE, saved to `.greenlit/<name>/<type>.xml`. Implementation is a template string module (`draft_meta.py`) — no API calls, no new dependencies, works offline.
**Why:** flips the authoring direction to match how elicitation now works (agent drafts, human edits) while keeping greenlit zero-dependency.
**Tests:** meta-prompt contains the user's ask verbatim, all current section keys, and the DONE requirement.

### 3.4 Second skill: greenlit-Write — `src/greenlit/skills/skill_write.md`
~30-line skill teaching an agent to *produce* greenlit files: when the user gives a fuzzy or multi-part task, draft a greenlit spec (all sections, DONE mandatory, EARS-style criteria), show it for confirmation, save under `.greenlit/`, then execute it per greenlit-Read.
- `init_cmd.py`: install both skills (greenlit-Read + greenlit-Write) per target; update wheel smoke test in CI to assert both files ship.

### 3.5 Review mode: `greenlit review <file>`
Load an existing greenlit file (parse both formats — a small `parser.py` with round-trip tests against the formatters), then reuse the existing walkthrough loop with content pre-filled. Reframe on-screen guidance as review checklists (same tips; new framing line: "Check the draft against these").
**Why:** repurposes ~all of display.py for the new authoring direction: agent drafts (3.3/3.4), human reviews here.
**Sequencing note:** 3.5 depends on the parser; build parser + round-trip tests first within this phase.

**Phase acceptance:** end-to-end flow works: `greenlit draft` → agent produces file (simulated in tests) → `greenlit review` opens it → DONE section drives verification per updated skill.

---

## Phase 4 — Positioning & distribution

### 4.1 Ship to real PyPI
Extend the release workflow from TestPyPI to PyPI (Trusted Publishing, tag-triggered). Verify `uvx greenlit` works from a clean machine. Un-comment and correct the README install section.
**This is the single highest-impact item in the whole plan for adoption.**

### 4.2 README rewrite
Reposition from "prompt walkthrough CLI" to "the lightweight spec layer for medium-sized AI tasks": agent drafts, human reviews, agent verifies against DONE. Lead with `uvx greenlit` and the draft → review → execute loop; walkthrough demoted to "manual mode."

### 4.3 Version & changelog
Bump to 0.2.0. CHANGELOG: document the changes — DELEGATION removed, JSON removed, YAML templates removed, gitignore default reversed. No compatibility shims anywhere: pre-1.0 and unpublished, old-format files are simply invalid.

---

## Out of scope (do not build)

- Any API-calling / model-invoking features inside greenlit itself (draft mode emits text only).
- Rerun/diff/history machinery beyond `list`/`show`.
- New runtime dependencies. rich remains the only one.
- Reintroducing custom task types in any form.
- TUI framework changes, color/theming work, Windows terminal QA beyond the clipboard fix.

## Global acceptance criteria

- CI green on 3.11/3.12/3.13; ruff clean; wheel smoke test passes and asserts **both** skill files in the wheel.
- Test count does not decrease relative to post-Phase-1 baseline (cuts remove tests; new features must add them).
- `greenlit` with no args still launches the interactive walkthrough (now eight sections, two formats).
- README, `--help` output, and skill files agree with actual behavior everywhere.

---

## Commit plan

Conventional Commits style. One commit per change, in this order. 3.5 is two commits (parser lands before the command that uses it).

| Change | Commit message |
|---|---|
| 0.0 | `docs: track and update CLAUDE.md project router` |
| 0.1 | `fix(cli): run clipboard command on macOS and Windows in _copy_to_clipboard` |
| 0.2 | `fix(init): install Copilot instructions to repo-level .github/instructions/` |
| 0.3 | `feat(init): add project-level .claude/skills install target` |
| 0.4 | `chore(init): replace deprecated importlib.resources.read_text with files()` |
| 0.5 | `refactor(cli): extract save/picker helpers and hoist guidance lookup` |
| 1.1 | `feat(sections): remove DELEGATION section from format, guidance, and skill` |
| 1.2 | `feat(formatters): drop JSON output format` |
| 1.3 | `feat: remove YAML custom template system and pyyaml extra` |
| 2.1 | `feat(cli): add non-interactive new subcommand with --set section values` |
| 2.2 | `feat(cli): add --stdout mode with UI chrome routed to stderr` |
| 2.3 | `feat(cli): version .greenlit/ by default; add --private gitignore opt-in` |
| 2.4 | `feat(formatters): stamp greenlit version in emitted artifacts` |
| 2.5 | `feat(cli): add list and show subcommands for the .greenlit/ library` |
| 3.1 | `feat(sections): add DONE verification section and enforce it in skill protocol` |
| 3.2 | `feat(cli): add --lite three-section walkthrough (ASK, SCOPE, DONE)` |
| 3.3 | `feat(cli): add draft subcommand emitting agent-authoring meta-prompt` |
| 3.4 | `feat(skills): add greenlit-Write skill; install and ship both skills` |
| 3.5a | `feat(parser): add XML/Markdown prompt parser with round-trip tests` |
| 3.5b | `feat(cli): add review subcommand for stepping through drafted prompts` |
| 4.1 | `ci(release): publish to PyPI via trusted publishing on tags` |
| 4.2 | `docs(readme): reposition as lightweight spec layer; lead with uvx install` |
| 4.3 | `chore(release): bump version to 0.2.0 and finalize changelog` |
