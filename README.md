# greenlit

[![CI](https://github.com/abali2509/greenlit/actions/workflows/ci.yml/badge.svg)](https://github.com/abali2509/greenlit/actions/workflows/ci.yml)
[![Release](https://github.com/abali2509/greenlit/actions/workflows/release.yml/badge.svg)](https://github.com/abali2509/greenlit/actions/workflows/release.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Structure prompts before you burn tokens.

A CLI walkthrough that guides you through nine prompt sections — ASK, GOAL, CONTEXT, SCOPE, DELEGATION, INPUTS, OUTPUTS, CONSTRAINT, ATTENTION — with task-specific guidance at every step.

---

## Install

Requires **Python 3.11+**.

### From source

```bash
git clone https://github.com/abali2509/greenlit.git
cd greenlit

# using uv (recommended)
uv sync
uv sync --extra templates        # adds YAML template support

# or using pip
pip install -e .
pip install -e ".[templates]"    # adds YAML template support
```

### Global install

To use `greenlit` as a standalone command without prefixing `uv run`:

**uv tool** (recommended if you use uv):
```bash
uv tool install .                      # from source
uv tool install ".[templates]"        # with YAML template support
```

**pipx**:
```bash
pipx install .                         # from source
pipx install ".[templates]"           # with YAML template support
```

Both methods install `greenlit` into an isolated environment and add it to `~/.local/bin`. Make sure `~/.local/bin` is on your `PATH`.

<!-- ### From PyPI (coming soon)
```bash
pip install greenlit
pip install "greenlit[templates]"
``` -->

---

## Agent skill setup

Run `greenlit init` once inside a project to install the bundled agent skill:

```bash
greenlit init
```

You are prompted to choose a target:

| Option | Destination | Agent |
|--------|-------------|-------|
| `1` | `.claude/skills/greenlit-Read/SKILL.md` | Claude Code |
| `2` | `.github/read-greenlit-prompt.md` | GitHub Copilot |

The skill teaches your agent how to read and execute greenlit prompt files. After installation, invoke it with `/greenlit-Read` in Claude Code.

---

## Quick start

```bash
# interactive — pick task type at the prompt
greenlit

# skip the selector
greenlit -t review
greenlit -t plan
greenlit -t action
greenlit -t debug
greenlit -t research

# set output format
greenlit -t action -o json

# save to a specific file
greenlit -t debug -o xml -f prompt.xml

# copy to clipboard after saving
greenlit -t review -c

# set a prompt name and output directory
greenlit -t action -n auth-refactor
greenlit -t action -n auth-refactor -d prompts/

# use inline input instead of opening an editor
greenlit -t debug --no-editor

# use a custom YAML template
greenlit -T my_template.yaml
```

Prompts are saved as `<dir>/<name>/<type>.<ext>` — by default `.greenlit/<name>/<type>.<ext>`. Use `-n` to set the name slug, `-d` to change the root directory, or `-f` to specify an exact path. If the same path already exists, a counter suffix is appended (`action_2.md`, `action_3.md`, …).

If installed with uv, prefix commands with `uv run`:

```bash
uv run greenlit
uv run greenlit -t action -o json
```

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

## Output formats

**XML** (default saves as `.xml`):
```xml
<prompt type="review">
  <ask>Review the auth module for correctness and edge cases.</ask>
  <goal>Catch any issues before the release cut.</goal>
</prompt>
```

**Markdown** (saves as `.md`):
```markdown
# REVIEW PROMPT

## ASK
Review the auth module for correctness and edge cases.

## GOAL
Catch any issues before the release cut.
```

**JSON** (saves as `.json`):
```json
{
  "sections": {
    "ask": "Review the auth module for correctness and edge cases.",
    "goal": "Catch any issues before the release cut."
  },
  "type": "review"
}
```

---

## Custom templates

Create a YAML file to define a custom task type:

```yaml
name: dbt_review
label: dbt Review
icon: "custom"
description: Review dbt models and pipeline code
extends: review        # fall back to this built-in type for any unspecified sections
sections:
  ask:
    hint: "Which models or macros are you reviewing?"
    placeholder: "Review staging models for naming conventions..."
    tips:
      - "Reference the specific model file paths"
  goal:
    hint: "What quality bar for this dbt layer?"
    placeholder: "Ensure ref() usage is correct..."
    tips:
      - "Mention whether you care about performance or correctness"
```

Run it:

```bash
greenlit -T dbt_review.yaml
```

Sections not defined in the YAML inherit from the `extends` type. Requires `pip install "greenlit[templates]"`.

---

## Section reference

| Section | Purpose |
|---------|---------|
| ASK | What exactly do you want done? |
| GOAL | Why are you doing this? What does success look like? |
| CONTEXT | Background the agent needs to do good work. |
| SCOPE | Hard boundaries — what's in, what's out. |
| DELEGATION | Agent roles for sub-tasks — who does what. |
| INPUTS | What material is being provided? |
| OUTPUTS | What deliverables do you expect back? |
| CONSTRAINT | Hard rules. Non-negotiable requirements. |
| ATTENTION | Red flags, edge cases, things that look fine but aren't. |

---

## Nav commands

Inside the walkthrough, at any `>` prompt:

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
