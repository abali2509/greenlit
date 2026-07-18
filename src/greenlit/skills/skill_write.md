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

## Default constraints

Every task type carries baseline constraints that guard its classic failure mode. **Include the matching type's lines verbatim in the drafted spec's CONSTRAINT section**, then add any others the ask calls for. Present them as pre-filled defaults the user can amend or delete when they confirm the spec — they are a starting point, not a verdict.

| Task type | Default constraints |
|---|---|
| `review` | Read-only: do not create, modify, or commit any files. · Report findings, do not fix them. · Every finding must reference a file and line. |
| `plan` | Do not implement anything — the plan is the only output. · Surface assumptions and open questions explicitly rather than resolving them silently. |
| `action` | Change nothing outside SCOPE. · Do not add or upgrade dependencies without flagging first. · If a DONE criterion cannot be met, stop and report — never redefine done. |
| `debug` | Reproduce the failure before changing anything. · Fix the root cause with the smallest change; no opportunistic refactoring. · Never modify or delete tests to make them pass. |
| `research` | Do not modify the codebase. · Distinguish verified fact from inference. · Cite sources for external claims. |
| `docs` | Modify only documentation files; never change code behavior. · Match the existing documentation's voice and conventions. · Verify that examples and commands in the docs actually run. |

**These constraints live in the spec, never applied out-of-band.** You write them into the CONSTRAINT section where the user can see, edit, or remove them — the saved spec remains the complete contract. Do not silently enforce a constraint at execution time that isn't written in the file, and do not omit a default from the file on the assumption you'll "just follow it anyway."

## Protocol

1. **Elicit what's missing.** Ask focused clarifying questions to fill gaps you cannot safely infer — especially GOAL, SCOPE boundaries, and how DONE will be verified. Ask only what you need.
2. **Draft the spec** in XML with `<prompt type="..." greenlit="0.2">`, seeding CONSTRAINT with the task type's default constraints (above).
3. **Show it to the user and confirm** before saving. Let them correct it.
4. **Save it** to `.greenlit/<name>/<type>.xml`.
5. **Execute it** following the greenlit-Read protocol — including running every DONE criterion and reporting pass/fail before declaring completion.

Never declare the task done without executing DONE.
