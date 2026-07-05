"""Meta-prompt generation for `greenlit draft` — agent-first authoring.

Emits a text prompt instructing an agent to interview the user and produce a
valid greenlit spec. No API calls, no dependencies — a pure string builder.
"""

from greenlit.sections import SECTIONS, TASK_TYPES


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
    else:
        type_labels = ", ".join(f"`{k}`" for k in TASK_TYPES)
        type_line = (
            f"Infer the most fitting task type from the ask. Choose one of: "
            f"{type_labels}."
        )
        type_attr = "<inferred-type>"
        name_hint = "<slug>"

    return f"""\
You are authoring a **greenlit spec** — a structured task specification — on
behalf of the user. Your job is to turn a one-line ask into a complete,
reviewable spec, then save it.

## The user's ask

{ask}

## What to do

1. **Interview the user about gaps.** The one-line ask above is underspecified.
   Ask focused clarifying questions to fill in what you cannot safely infer:
   goals, boundaries, inputs, expected outputs, constraints, and — critically —
   how completion will be verified. Ask only what you genuinely need; do not
   interrogate.
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

Do not begin executing the task itself — your only job here is to produce the
spec and save it for the user to greenlit.
"""
