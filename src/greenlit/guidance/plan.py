"""Guidance for the 'plan' task type."""

from greenlit.sections import SectionGuidance

GUIDANCE: dict[str, SectionGuidance] = {
    "ask": SectionGuidance(
        hint=(
            "What system, feature, or migration needs designing? "
            "Be specific about the deliverable."
        ),
        placeholder=(
            "Design the orchestrator-agent architecture for our async pipeline "
            "runner, producing a task graph and interface contracts."
        ),
        tips=[
            "Distinguish between 'plan the approach' and 'produce a spec'",
            "Name the system boundary — what are you designing within?",
            "If incremental, state what exists and what's new",
        ],
    ),
    "goal": SectionGuidance(
        hint="What problem does this solve? What does 'done well' look like?",
        placeholder=(
            "Enable parallel execution of independent pipeline tasks, "
            "reducing end-to-end runtime by 60%+."
        ),
        tips=[
            "Quantify where possible — latency, throughput, coverage",
            "Distinguish must-haves from nice-to-haves",
            "Name the failure mode you're designing against",
        ],
    ),
    "context": SectionGuidance(
        hint="What exists today? What constraints does the current system impose?",
        placeholder=(
            "We currently run tasks sequentially in a single Python process. "
            "The codebase uses asyncio elsewhere."
        ),
        tips=[
            "Describe the current state honestly — warts and all",
            "Mention team familiarity with proposed tech",
            "Include integration points and dependencies",
            "Reference any prior art or rejected approaches",
        ],
    ),
    "scope": SectionGuidance(
        hint="What's in v1? What's explicitly deferred? What's never in scope?",
        placeholder=(
            "IN: Task graph, parallel execution, retry logic\n"
            "DEFERRED: Dynamic DAG modification\n"
            "OUT: Warehouse schema changes"
        ),
        tips=[
            "Use IN / DEFERRED / OUT explicitly",
            "Be specific about what 'deferred' means — v2? never? maybe?",
            "Name the integration boundaries — what you own vs don't",
        ],
    ),
    "delegation": SectionGuidance(
        hint="Break the design into sub-problems. Assign each to a specialist.",
        placeholder=(
            "Agent 1 — Task Graph: DAG structure and dependency resolution\n"
            "Agent 2 — Executor: parallel execution engine\n"
            "Agent 3 — Resilience: retry, timeout, failure handling"
        ),
        tips=[
            "Fan-out to specialist agents, fan-in to a synthesiser",
            "Define the interface contract between agents",
            "Specify which agent has final say on trade-offs",
        ],
    ),
    "inputs": SectionGuidance(
        hint="Requirements, existing code, diagrams, constraints docs.",
        placeholder=(
            "- Current runner: pipeline/runner.py\n"
            "- Task interface: tasks/base.py\n"
            "- RFC: docs/parallel-execution-rfc.md"
        ),
        tips=[
            "Include existing interfaces the design must respect",
            "Provide any RFCs, ADRs, or design docs",
            "Reference similar implementations if they exist",
        ],
    ),
    "outputs": SectionGuidance(
        hint="The shape of the design deliverable.",
        placeholder=(
            "Architecture overview, interface contracts (Python ABCs), "
            "task breakdown with estimates, risk register, open questions"
        ),
        tips=[
            "Ask for diagrams if the system has moving parts",
            "Request interface definitions, not just descriptions",
            "Include a task breakdown if this feeds into sprint planning",
        ],
    ),
    "constraint": SectionGuidance(
        hint="Technical, team, and business constraints the design must respect.",
        placeholder=(
            "Single Python process. Backwards-compatible with existing tasks. "
            "Max 2 new deps. Cold-start increase < 5s."
        ),
        tips=[
            "State infrastructure constraints (single process, memory limits)",
            "Mention backwards-compatibility requirements",
            "Include timeline and team capacity constraints",
        ],
    ),
    "attention": SectionGuidance(
        hint="Failure modes, integration risks, things easy to underestimate.",
        placeholder=(
            "asyncio task cancellation is tricky — plan for cleanup. "
            "Task interface assumes sync — adapting may have hidden coupling. "
            "Datadog 512 event/s limit."
        ),
        tips=[
            "Name the thing that will bite you at 2am",
            "Mention dependencies that are flaky or poorly documented",
            "Flag assumptions that seem safe but might not be",
        ],
    ),
}
