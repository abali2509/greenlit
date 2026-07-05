---
name: greenlit-Write
description: Use this skill when the user hands you a fuzzy, underspecified, or multi-part task and it would benefit from a structured spec before execution. Teaches you to author a greenlit prompt (nine sections, DONE mandatory), confirm it, save it under `.greenlit/`, then execute it.
---

# Authoring a greenlit spec

When a task is vague, large, or has several moving parts, don't dive straight in. Draft a **greenlit spec** first — a structured task specification the user can review before you commit effort. This is the write-side counterpart to greenlit-Read.

## When to use

- The ask is one line but the work is not trivial.
- The task has multiple parts, unclear boundaries, or unstated success criteria.
- Getting it wrong would be expensive to redo.

If the task is small and unambiguous, skip this — just do it.

## The nine sections

Author in XML with these keys, in order: `ask`, `goal`, `context`, `scope`, `inputs`, `outputs`, `constraint`, `attention`, `done`.

- Fill only the sections you have real content for — never invent filler.
- **DONE is mandatory.** It holds testable acceptance criteria: prefer EARS-style ("WHEN <condition>, the system SHALL <behavior>") and runnable checks (a test command, a lint command, a checklist). A spec without a verifiable DONE is incomplete.

## Protocol

1. **Elicit what's missing.** Ask focused clarifying questions to fill gaps you cannot safely infer — especially GOAL, SCOPE boundaries, and how DONE will be verified. Ask only what you need.
2. **Draft the spec** in XML with `<prompt type="..." greenlit="0.2">`.
3. **Show it to the user and confirm** before saving. Let them correct it.
4. **Save it** to `.greenlit/<name>/<type>.xml`.
5. **Execute it** following the greenlit-Read protocol — including running every DONE criterion and reporting pass/fail before declaring completion.

Never declare the task done without executing DONE.
