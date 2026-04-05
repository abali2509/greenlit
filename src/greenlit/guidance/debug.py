"""Guidance for the 'debug' task type."""

from greenlit.sections import SectionGuidance

GUIDANCE: dict[str, SectionGuidance] = {
    "ask": SectionGuidance(
        hint="Describe the symptom. Observed vs expected behaviour in one sentence.",
        placeholder=(
            "The pipeline fails silently on incremental loads — no error raised, "
            "no rows written, exit code 0."
        ),
        tips=[
            "State what you observed, not what you think the cause is",
            "Include the exact error message or anomaly if one exists",
            "Note when it started — after a deploy? a config change? randomly?",
        ],
    ),
    "goal": SectionGuidance(
        hint="Root cause identified and fix validated. What does 'resolved' look like?",
        placeholder=(
            "Identify why rows are silently dropped and confirm fix with a "
            "reproducing test case."
        ),
        tips=[
            "Distinguish 'understand the cause' from 'ship a fix' — sometimes you "
            "just need the diagnosis",
            "State whether you need a hotfix or a proper fix",
            "Mention who needs to be notified when it's resolved",
        ],
    ),
    "context": SectionGuidance(
        hint="Logs, error traces, timeline of when it broke, recent deploys or config changes.",
        placeholder=(
            "Broke after deploy v2.3.1 on 2024-03-15. No schema changes. "
            "Logs show zero rows processed but no exception."
        ),
        tips=[
            "Paste the full stack trace — truncated traces hide root causes",
            "Include timestamps and environment (prod/staging/local)",
            "Note what changed recently — deploys, config, data volume, dependencies",
            "List what you've already ruled out",
        ],
    ),
    "scope": SectionGuidance(
        hint="Where to look first. What's already been ruled out.",
        placeholder=(
            "IN: pipeline/loader.py, the incremental load logic\n"
            "RULED OUT: network connectivity, source data schema\n"
            "OUT: dbt models — confirmed working"
        ),
        tips=[
            "Narrow the blast radius — which component changed? start there",
            "List what you've already checked so the agent doesn't retread",
            "Use IN / RULED OUT / OUT explicitly",
        ],
    ),
    "delegation": SectionGuidance(
        hint="Split the investigation by subsystem or hypothesis if parallel diagnosis helps.",
        placeholder=(
            "Agent 1 — Trace the data path through loader.py\n"
            "Agent 2 — Check recent dependency changes for silent-failure "
            "regressions\n"
            "Agent 3 — Reproduce locally with minimal test case"
        ),
        tips=[
            "Assign each agent a distinct hypothesis to validate",
            "Define how agents report findings — confidence level, evidence",
            "One agent should own writing the reproducing test case",
        ],
    ),
    "inputs": SectionGuidance(
        hint="Error traces, metrics dashboards, recent deploy diffs, relevant source files.",
        placeholder=(
            "- Stack trace: (paste below)\n"
            "- Metrics: Datadog dashboard link\n"
            "- Deploy diff: github.com/org/repo/compare/v2.3.0...v2.3.1\n"
            "- Source: pipeline/loader.py"
        ),
        tips=[
            "Include the full log output, not a summary",
            "Attach or link the deploy diff — this is often where the bug lives",
            "Reference dashboards or alerting that surfaced the issue",
        ],
    ),
    "outputs": SectionGuidance(
        hint="Root cause analysis, fix recommendation, and confidence level.",
        placeholder=(
            "Root cause with evidence, minimal reproducing test case, "
            "recommended fix, confidence (high/medium/low), follow-up risks"
        ),
        tips=[
            "Ask for a confidence level — 'I think' vs 'I confirmed'",
            "Request a reproducing test case, not just a theory",
            "Ask the agent to flag any related risks uncovered during investigation",
        ],
    ),
    "constraint": SectionGuidance(
        hint="Production constraints, rollback options, time pressure.",
        placeholder=(
            "Cannot restart the pipeline mid-run. Fix must be backwards-compatible. "
            "Need resolution within 2 hours (SLA breach at 18:00)."
        ),
        tips=[
            "State if there's a hard deadline or SLA in play",
            "Note rollback options — can you revert the deploy?",
            "Flag if the system is currently down vs degraded",
        ],
    ),
    "attention": SectionGuidance(
        hint="Known red herrings. Similar past incidents. Misleading signals.",
        placeholder=(
            "Exit code 0 is expected even on partial failure — check row count "
            "metrics, not just process exit. Similar incident in Jan: was a "
            "silent schema mismatch."
        ),
        tips=[
            "Name past incidents that looked the same but had different causes",
            "Flag metrics or signals that are misleading in this system",
            "Warn about any 'obvious' fixes that were tried and didn't work",
        ],
    ),
}
