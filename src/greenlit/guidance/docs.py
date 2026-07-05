"""Guidance for the 'docs' task type."""

from greenlit.sections import SectionGuidance

DEFAULT_CONSTRAINTS: list[str] = [
    "Modify only documentation files; never change code behavior.",
    "Match the existing documentation's voice and conventions.",
    "Verify that examples and commands in the docs actually run.",
]

GUIDANCE: dict[str, SectionGuidance] = {
    "ask": SectionGuidance(
        hint="What documentation needs writing, updating, or restructuring? Name the artefact.",
        placeholder=(
            "Update the README install section and add a quickstart guide "
            "for the new CLI subcommands."
        ),
        tips=[
            "Name the specific file(s) or doc surface — README, API ref, guide, docstrings",
            "State whether it's net-new, an update, or a restructure",
            "If updating, say what changed in the product that the docs must catch up to",
        ],
    ),
    "goal": SectionGuidance(
        hint="Who reads this and what should they be able to do after? Define 'good docs' here.",
        placeholder=(
            "A first-time user can install and run their first command in "
            "under five minutes without reading the source."
        ),
        tips=[
            "Name the audience — new user, integrator, contributor, maintainer",
            "State the outcome: what can the reader do that they couldn't before?",
            "Distinguish reference (look-up) from guide (learn-by-doing)",
        ],
    ),
    "context": SectionGuidance(
        hint="Where do the docs live, what's the house style, and what already exists?",
        placeholder=(
            "Docs are Markdown under docs/, built with mkdocs. Voice is terse and "
            "second-person. Existing quickstart at docs/getting-started.md."
        ),
        tips=[
            "Point to the docs toolchain (mkdocs, Sphinx, plain Markdown)",
            "Reference the existing style guide or a doc that exemplifies the voice",
            "List related docs so the new content links in, not orphaned",
        ],
    ),
    "scope": SectionGuidance(
        hint="Which docs are in scope? What stays untouched? Where does the edit stop?",
        placeholder=(
            "IN: README install + quickstart\n"
            "OUT: API reference (auto-generated)\n"
            "DEFERRED: migration guide"
        ),
        tips=[
            "Name the exact files in scope; docs sprawl fast",
            "State what NOT to touch — auto-generated pages, changelog, licence",
            "Use IN / OUT / DEFERRED explicitly",
        ],
    ),
    "inputs": SectionGuidance(
        hint="Source material the writer needs: the feature, the code, existing drafts.",
        placeholder=(
            "- CLI help output: `greenlit --help`\n"
            "- Feature PR: #42\n"
            "- Current README.md\n"
            "- Style reference: docs/getting-started.md"
        ),
        tips=[
            "Provide the command output or code the docs describe",
            "Link the PR or spec that introduced the behaviour",
            "Include a doc that models the target voice",
        ],
    ),
    "outputs": SectionGuidance(
        hint="The exact docs deliverable: which files, what structure, what format.",
        placeholder=(
            "Updated README.md install section, new docs/quickstart.md with a "
            "runnable end-to-end example, cross-links from the index."
        ),
        tips=[
            "Name the files and their locations",
            "Specify structure — headings, code blocks, tables",
            "Say whether screenshots, diagrams, or runnable snippets are expected",
        ],
    ),
    "constraint": SectionGuidance(
        hint="Rules the docs must follow. Voice, format, and what must not change.",
        placeholder=(
            "Modify only documentation files. Match existing voice. "
            "Every command shown must actually run against the current version."
        ),
        tips=[
            "State the voice and person (second-person, present tense)",
            "Require that examples are tested, not illustrative-only",
            "Forbid touching code or behaviour to make the docs true",
        ],
    ),
    "attention": SectionGuidance(
        hint="Doc traps: stale examples, drifted flags, copy-paste that no longer runs.",
        placeholder=(
            "The old README shows `-o json` — that flag was removed in 0.2. "
            "Check every flag against `--help` before documenting it."
        ),
        tips=[
            "Flag examples that silently rotted after a code change",
            "Name flags, paths, or outputs that changed and must be re-verified",
            "Warn about version-specific claims that need a version note",
        ],
    ),
    "done": SectionGuidance(
        hint="How you'll prove the docs are correct and complete, not just written.",
        placeholder=(
            "- Every command block runs clean against the current build.\n"
            "- WHEN a new user follows the quickstart, they reach a working result "
            "with no external lookups.\n"
            "- No dead links; new pages are cross-linked from the index."
        ),
        tips=[
            "Make 'examples run' a checkable item — actually execute them",
            "Write EARS-style where behaviour is involved: WHEN <reader does X>, they SHALL <Y>",
            "Include link-check and cross-reference completeness",
        ],
    ),
}
