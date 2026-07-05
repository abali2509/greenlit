# greenlit

[![CI](https://github.com/abali2509/greenlit/actions/workflows/ci.yml/badge.svg)](https://github.com/abali2509/greenlit/actions/workflows/ci.yml)
[![Release](https://github.com/abali2509/greenlit/actions/workflows/release.yml/badge.svg)](https://github.com/abali2509/greenlit/actions/workflows/release.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**The lightweight spec layer for medium-sized AI tasks.** The agent drafts a structured spec, you review it, the agent executes it and verifies its own work against testable DONE criteria.

Bigger than a one-line prompt, smaller than a design doc — greenlit owns the middle ground where a little structure turns a fuzzy ask into a first-pass-correct result.

```bash
uvx greenlit draft "add rate limiting to the public API"
```

That emits a meta-prompt you hand to your coding agent. It interviews you about the gaps, writes a nine-section spec to `.greenlit/`, and — once you greenlit it — executes and checks off every DONE criterion.

---

## Install

Requires **Python 3.11+**.

Run without installing (recommended):

```bash
uvx greenlit                # interactive walkthrough
uvx greenlit draft "<ask>"  # agent-authoring meta-prompt
```

Install as a standalone command:

```bash
uv tool install greenlit    # via uv
pipx install greenlit       # via pipx
pip install greenlit        # into the current environment
```

`uv tool` and `pipx` install into an isolated environment on your `PATH` (usually `~/.local/bin`).

---

## The spec format

A greenlit spec is nine sections, each answering one question. Only fill what applies — but **DONE is what makes the loop close.**

| Section | Purpose |
|---------|---------|
| ASK | What exactly do you want done? |
| GOAL | Why? What does success look like? |
| CONTEXT | Background the agent needs to do good work. |
| SCOPE | Hard boundaries — what's in, what's out. |
| INPUTS | What material is being provided? |
| OUTPUTS | What deliverables do you expect back? |
| CONSTRAINT | Hard rules. Non-negotiable requirements. |
| ATTENTION | Red flags, edge cases, things that look fine but aren't. |
| DONE | Testable acceptance criteria. How the agent proves it's finished. |

Specs are saved as `.greenlit/<name>/<type>.<ext>` in XML or Markdown, stamped with the format version:

```xml
<prompt type="action" greenlit="0.2">
  <ask>Add rate limiting to the public API endpoints.</ask>
  <scope>Middleware only; no route changes.</scope>
  <done>WHEN 100 req/s hit /api, excess requests SHALL receive HTTP 429.
        `pytest tests/test_ratelimit.py` passes.</done>
</prompt>
```

### Writing good DONE criteria (EARS)

DONE works best as **EARS-style** requirements — objectively checkable, not aspirational. The two common shapes:

- **WHEN** `<trigger>`, the system SHALL `<behavior>` — for event-driven behavior.
- **IF** `<condition>`, the system SHALL `<behavior>` — for handling an unwanted or exceptional state.

> WHEN a request exceeds the rate limit, the system SHALL respond with HTTP 429 and a `Retry-After` header.

Prefer runnable checks where possible — a test command, a lint command, or a concrete checklist. A spec whose DONE can't be evaluated isn't done.

---

## The seven flows

### 1. Draft → review → execute → verify (the flagship loop)

Turn a one-line ask into a verified result. The agent does the writing; you do the reviewing.

```bash
greenlit draft "add rate limiting to the public API" | claude -p
```

The agent interviews you about gaps, writes the spec to `.greenlit/rate-limit/action.xml`, then you check it:

```bash
greenlit review .greenlit/rate-limit/action.xml
```

Step through each section as a review checklist, correct anything, save. The agent then executes it per the greenlit-Read skill — running every DONE criterion and reporting pass/fail before it declares completion.

### 2. Skills-only, no CLI

You don't have to install anything. Run `greenlit init` once to drop the **greenlit-Write** skill into your agent, and it triggers itself: hand your agent a fuzzy or multi-part task mid-session and it drafts a spec, confirms it with you, saves it under `.greenlit/`, and executes it. Everything below works even for teammates who never install the package.

### 3. Full manual walkthrough

For big, novel, or high-stakes tasks — all nine sections, guided:

```bash
greenlit                    # pick task type at the prompt
greenlit -t action          # skip the selector
```

### 4. Lite walkthrough

For medium tasks — just ASK, SCOPE, DONE, in about two minutes:

```bash
greenlit --lite
```

### 5. Scripted one-shot

For scripts, hooks, CI, and other agents — build a spec non-interactively and pipe it straight into a model:

```bash
greenlit new -t action \
  --set ask="Add rate limiting to public API endpoints" \
  --set done="WHEN 100 req/s hit /api, excess SHALL get 429; pytest passes" \
  --stdout | claude -p
```

`--set key=-` reads that section's content from stdin. With `--stdout`, the formatted spec goes to stdout and all UI chrome to stderr, so the pipe stays clean.

### 6. Library & reuse

`.greenlit/` is committed by default — your specs are diffed in PRs as the project's record of intent.

```bash
greenlit list                          # name, type, format, modified
greenlit show .greenlit/rate-limit/action.xml
```

(Use `--private` at creation time to add `.greenlit/` to `.gitignore` instead.)

### 7. Setup & onboarding

Install the agent skills once:

```bash
greenlit init
```

Choose where they land:

| Option | Destination | Agent |
|--------|-------------|-------|
| `1` | `~/.claude/skills/` | Claude Code (user-global) |
| `2` | `.claude/skills/` | Claude Code (project-level — clone the repo, inherit the skills) |
| `3` | `.github/instructions/` | GitHub Copilot (repo-level) |

Both **greenlit-Read** (execute a spec) and **greenlit-Write** (author one) are installed per target.

---

## Which flow?

- **Fuzzy task, mid-session** → flow 2 (let the skill draft it).
- **Defined task worth structuring** → flow 1 (draft → review → execute → verify).
- **Quick task** → flow 4 (`--lite`).
- **Big, novel task** → flow 3 (full walkthrough).
- **Automation / scripts / other agents** → flow 5 (`new --stdout`).

---

## Task types

| Type | Description |
|------|-------------|
| `review` | Code review, PR review, architecture review |
| `plan` | Architecture, design, task breakdown |
| `action` | Implementation, refactoring, migration |
| `debug` | Diagnose failures, trace bugs, root cause analysis |
| `research` | Spikes, investigations, trade-off analysis |

---

## Nav commands

Inside the walkthrough (and `review`), at any `>` prompt:

| Command | Action |
|---------|--------|
| `n` / `next` | Move to next section |
| `b` / `back` | Go back one section |
| `s` / `skip` | Skip this section |
| `p` / `preview` | Preview current output |
| `e` / `edit` | Jump to a specific section |
| `q` / `quit` | Quit (prompts to save if content exists, else exits) |

---

## Contributing

Issues and PRs welcome at https://github.com/abali2509/greenlit.

---

## License

MIT
