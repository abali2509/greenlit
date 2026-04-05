"""Guidance for the 'review' task type."""

from greenlit.sections import SectionGuidance

GUIDANCE: dict[str, SectionGuidance] = {
    "ask": SectionGuidance(
        hint=(
            "Clear verb + object. One sentence. What are you reviewing and "
            "what's the focus?"
        ),
        placeholder=(
            "Review the data pipeline module for correctness, error handling, "
            "and adherence to our dbt patterns."
        ),
        tips=[
            "Name the specific artefact (file, PR, module, RFC)",
            "State the review lens — security? performance? readability? all?",
            "If it's a re-review, say what changed since last pass",
        ],
    ),
    "goal": SectionGuidance(
        hint="What quality bar are you holding this against? What would a successful review catch?",
        placeholder=(
            "Ensure the pipeline is production-ready: no silent failures, "
            "clear lineage, idempotent runs."
        ),
        tips=[
            "State the quality bar explicitly — 'production-ready' means "
            "different things",
            "Mention what a miss looks like — what would be bad to ship?",
            "If there's a deadline or release gate, say so",
        ],
    ),
    "context": SectionGuidance(
        hint=(
            "What does the reviewer need to know about the codebase, "
            "the change, and the motivation?"
        ),
        placeholder=(
            "This module was extracted from a monolithic ETL script last sprint. "
            "It handles incremental loads from 3 sources."
        ),
        tips=[
            "Explain the 'why' behind the change — not just the 'what'",
            "Mention recent related changes or known tech debt",
            "If there are conventions or patterns the code should follow, state "
            "them",
            "Include the tech stack versions if relevant",
        ],
    ),
    "scope": SectionGuidance(
        hint="Which files or concerns to focus on? What to explicitly ignore?",
        placeholder=(
            "IN: pipeline/loader.py, pipeline/lineage.py\n"
            "OUT: Don't review dbt models — separate process."
        ),
        tips=[
            "List specific files or directories",
            "Name concerns that are out of scope for this review",
            "If it's a large PR, prioritise which files matter most",
        ],
    ),
    "delegation": SectionGuidance(
        hint="Split the review into specialised passes if needed.",
        placeholder=(
            "Agent 1 — Correctness: logic, edge cases, error handling\n"
            "Agent 2 — Patterns: conventions, dbt best practices\n"
            "Agent 3 — Observability: logging, metrics, lineage"
        ),
        tips=[
            "Each agent should have a clear, non-overlapping concern",
            "Name the expertise each agent needs",
            "Specify how agents should report — inline comments? summary? "
            "severity?",
        ],
    ),
    "inputs": SectionGuidance(
        hint="The code, diffs, docs, and reference material the reviewer needs.",
        placeholder=(
            "- PR diff (attached)\n"
            "- Test suite in tests/\n"
            "- Style guide: CONTRIBUTING.md"
        ),
        tips=[
            "Attach or reference the actual files",
            "Include the test suite — reviewers need to see coverage",
            "Provide the style guide or conventions doc if one exists",
        ],
    ),
    "outputs": SectionGuidance(
        hint="Format and structure of the review feedback.",
        placeholder=(
            "Summary (2-3 sentences), findings list with severity/file:line/fix, "
            "verdict: approve/request changes/block"
        ),
        tips=[
            "Specify severity levels and what each means",
            "Ask for line-specific references",
            "Request a clear verdict, not just observations",
        ],
    ),
    "constraint": SectionGuidance(
        hint="Standards, policies, and non-negotiable quality bars.",
        placeholder=(
            "All SQL parameterised. Every external call has error handling. "
            "Logging via structlog only. No new deps without justification."
        ),
        tips=[
            "Include security requirements explicitly",
            "Reference the linter/formatter config if relevant",
            "State performance thresholds if applicable",
        ],
    ),
    "attention": SectionGuidance(
        hint="Known risks, subtle bugs, areas where mistakes are likely.",
        placeholder=(
            "Lineage tracker has a race condition under concurrency. "
            "Previous version silently dropped nulls. Retry logic caused "
            "duplicate inserts."
        ),
        tips=[
            "Flag known bugs or tech debt near the change",
            "Mention areas where the code 'looks fine' but has bitten you",
            "Highlight recent production incidents related to this code",
        ],
    ),
}
