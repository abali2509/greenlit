"""Meta-prompt generation for `greenlit draft` — agent-first authoring.

Emits a text prompt instructing an agent to interview the user and produce a
valid greenlit spec. No API calls, no dependencies — a pure string builder.
"""

from greenlit.guidance import get_default_constraints
from greenlit.sections import SECTIONS, TASK_TYPES


def _explicit_constraint_block(task_type: str) -> str:
    """Baseline-constraints instruction for a known task type."""
    lines = "\n".join(f"- {c}" for c in get_default_constraints(task_type))
    return (
        f"These baseline constraints are **required** for the `{task_type}` task "
        f"type — include them verbatim in the CONSTRAINT section, then add any "
        f"others the ask calls for:\n\n{lines}"
    )


def _inferred_constraint_block() -> str:
    """Baseline-constraints instruction covering every type, for inference."""
    blocks = []
    for t in TASK_TYPES:
        constraints = get_default_constraints(t)
        if not constraints:
            continue
        body = "\n".join(f"  - {c}" for c in constraints)
        blocks.append(f"- `{t}`:\n{body}")
    table = "\n".join(blocks)
    return (
        "Whichever task type you select, its baseline constraints are "
        "**required** — include that type's lines verbatim in the CONSTRAINT "
        "section, then add any others the ask calls for:\n\n" + table
    )


def build_meta_prompt(ask: str, task_type: str | None = None) -> str:
    """Return a meta-prompt telling an agent to author a greenlit spec for `ask`."""
    section_keys = [s.key for s in SECTIONS]
    keys_line = ", ".join(section_keys)

    if task_type:
        type_line = (
            f"The task type is `{task_type}`. Author the spec for that type."
        )
        type_attr = task_type
        name_hint = task_type
        constraint_block = _explicit_constraint_block(task_type)
    else:
        type_labels = ", ".join(f"`{k}`" for k in TASK_TYPES)
        type_line = (
            f"Infer the most fitting task type from the ask. Choose one of: "
            f"{type_labels}."
        )
        type_attr = "<inferred-type>"
        name_hint = "<slug>"
        constraint_block = _inferred_constraint_block()

    return f"""\
You are authoring a **greenlit spec** — a structured task specification — on
behalf of the user. Your job is to turn a one-line ask into a complete,
reviewable spec, then save it.

## The user's ask

{ask}

## What to do

1. **Fill the gaps.** The one-line ask above is underspecified. Identify what you
   cannot safely infer: goals, boundaries, inputs, expected outputs, constraints,
   and — critically — how completion will be verified.
   - **If you can interact with the user**, ask focused clarifying questions.
     Ask only what you genuinely need; do not interrogate.
   - **If you are running non-interactively (headless) and cannot get answers, do
     not stop and wait for a reply.** Proceed with explicit best-effort
     assumptions, label each one clearly, and record every unresolved question in
     the spec's ATTENTION section for the human to settle at review. A spec with
     flagged assumptions beats a blocked run that produces nothing.
2. **Draft the spec.** Once you have enough, produce a greenlit prompt in **XML**
   covering every section that applies. {type_line}
3. **Show it to the user for review** before saving. Let them correct it.
4. **Save it** to `.greenlit/{name_hint}/{type_attr}.xml`.

## Format

The XML must be:

```xml
<prompt type="{type_attr}" greenlit="0.2">
  <ask>...</ask>
  <goal>...</goal>
  ...
</prompt>
```

Valid section keys, in order: {keys_line}.

Only emit sections you have real content for — never invent filler. But the
**DONE** section is mandatory: it holds testable acceptance criteria (prefer
EARS-style "WHEN <condition>, the system SHALL <behavior>" and runnable checks
such as a test or lint command). A spec without a verifiable DONE is incomplete.

## Required constraints

{constraint_block}

Do not begin executing the task itself — your only job here is to produce the
spec and save it for the user to greenlit.
"""
