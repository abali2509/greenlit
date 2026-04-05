"""Guidance for the 'research' task type."""

from greenlit.sections import SectionGuidance

GUIDANCE: dict[str, SectionGuidance] = {
    "ask": SectionGuidance(
        hint=(
            "What specific questions must this spike answer? "
            "Not what to build — what to learn."
        ),
        placeholder=(
            "Is Temporal a better fit than our home-grown task queue for "
            "orchestrating async pipelines at our scale?"
        ),
        tips=[
            "Frame as questions to answer, not artefacts to produce",
            "If there are multiple questions, list them in priority order",
            "State the decision this research is informing",
        ],
    ),
    "goal": SectionGuidance(
        hint="Enough understanding to make a decision. State the decision and the timebox.",
        placeholder=(
            "Produce a recommendation on whether to adopt Temporal by end of "
            "sprint. Timebox: 3 days."
        ),
        tips=[
            "Name the decision explicitly — 'adopt X', 'choose between X and Y', "
            "'determine if X is feasible'",
            "Set a timebox — research without a deadline expands indefinitely",
            "Distinguish 'enough to decide' from 'full understanding'",
        ],
    ),
    "context": SectionGuidance(
        hint="Current setup, constraints that shape the decision, what's already been explored.",
        placeholder=(
            "We run 500+ tasks/day on a custom asyncio queue. Pain points: "
            "no retry UI, poor visibility, manual dead-letter handling."
        ),
        tips=[
            "Describe the current setup — what problem are you trying to solve?",
            "List constraints that eliminate options upfront (cost, language, ops "
            "burden)",
            "Note what's already been tried or ruled out and why",
        ],
    ),
    "scope": SectionGuidance(
        hint="The decision being informed. Depth limits. What adjacent areas to skip.",
        placeholder=(
            "IN: Temporal vs current queue — fit, migration cost, ops burden\n"
            "OUT: Airflow, Prefect — already evaluated\n"
            "DEPTH: Proof-of-concept only, not production sizing"
        ),
        tips=[
            "State the decision boundary — what are you choosing between?",
            "Set explicit depth limits — prototype, benchmarks, or paper research "
            "only?",
            "Name options that are already off the table to avoid retreading",
        ],
    ),
    "delegation": SectionGuidance(
        hint="Split by research axis — each agent investigates a distinct angle.",
        placeholder=(
            "Agent 1 — Evaluate Temporal: feature fit, SDK quality, operational "
            "complexity\n"
            "Agent 2 — Benchmark: throughput and latency at our task volume\n"
            "Agent 3 — Migration: effort estimate and risk assessment"
        ),
        tips=[
            "Each agent should own a distinct research question",
            "Define what 'done' looks like per agent — findings doc, benchmark "
            "results, go/no-go",
            "One agent should synthesise findings into a final recommendation",
        ],
    ),
    "inputs": SectionGuidance(
        hint="Existing docs, prior evaluations, benchmarks, source code to read.",
        placeholder=(
            "- Current queue impl: pipeline/queue.py\n"
            "- Prior spike notes: docs/queue-eval-2023.md\n"
            "- Temporal docs: docs.temporal.io\n"
            "- Load profile: avg 30 tasks/min, peak 200/min"
        ),
        tips=[
            "Include any prior research so the agent doesn't duplicate it",
            "Provide the load profile or scale numbers if doing benchmarks",
            "Reference the existing system's interface — what must the replacement "
            "match?",
        ],
    ),
    "outputs": SectionGuidance(
        hint="Findings, trade-off matrix, recommendation with confidence and rationale.",
        placeholder=(
            "Trade-off matrix (fit/cost/ops), go/no-go recommendation with "
            "confidence level, key risks, suggested next step"
        ),
        tips=[
            "Ask for a trade-off matrix, not just a narrative",
            "Request a confidence level — 'I'm 80% confident because...'",
            "Ask for the suggested next step: prototype, RFP, adopt, defer",
        ],
    ),
    "constraint": SectionGuidance(
        hint="Timebox, depth limits, and constraints that shape valid options.",
        placeholder=(
            "Max 3 days. No new managed services without infra team sign-off. "
            "Must support Python SDK. Self-hosted only."
        ),
        tips=[
            "Re-state the timebox here as a hard constraint",
            "List non-negotiable requirements that eliminate options",
            "Note approval gates that affect the recommendation",
        ],
    ),
    "attention": SectionGuidance(
        hint="Biases, known unknowns, and past experiences that might skew the research.",
        placeholder=(
            "Team has strong asyncio familiarity — don't overweight familiarity "
            "vs fit. Temporal has a steep ops curve at small scale."
        ),
        tips=[
            "Name cognitive biases likely to affect the research (familiarity, "
            "recency)",
            "Flag known unknowns — what might you not know you don't know?",
            "Mention past decisions that went wrong and what to avoid repeating",
        ],
    ),
}
