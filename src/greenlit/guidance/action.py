"""Guidance for the 'action' task type."""

from greenlit.sections import SectionGuidance

GUIDANCE: dict[str, SectionGuidance] = {
    "ask": SectionGuidance(
        hint="What needs building, fixing, or changing? Concrete verb, concrete target.",
        placeholder=(
            "Implement the fan-out/fan-in task executor using asyncio, with "
            "retry logic and structured logging."
        ),
        tips=[
            "One ask per prompt — split compound tasks into separate prompts",
            "Include the 'shape' of the work: new file, refactor, extend, fix",
            "If fixing, describe the current broken behaviour",
        ],
    ),
    "goal": SectionGuidance(
        hint="What's the measurable outcome? How will you know it works?",
        placeholder=(
            "Working executor that passes the test suite, handles 50+ concurrent "
            "tasks, logs to our observability stack."
        ),
        tips=[
            "Include acceptance criteria if you have them",
            "State the test: 'I'll know it works when...'",
            "Mention downstream effects — who/what depends on this",
        ],
    ),
    "context": SectionGuidance(
        hint="What does the implementer need to know to write correct code first time?",
        placeholder=(
            "Python 3.11, asyncio for concurrency, structlog for logging, "
            "pytest for tests. Task interface in tasks/base.py."
        ),
        tips=[
            "Paste or reference the relevant interfaces/types",
            "Mention the test framework and how to run tests",
            "Include env setup if non-obvious",
            "State which files/modules are relevant",
        ],
    ),
    "scope": SectionGuidance(
        hint="Exactly what to build. What not to touch. Where the work stops.",
        placeholder=(
            "Build the executor module only. Don't modify the task interface. "
            "Unit tests, not integration tests."
        ),
        tips=[
            "State what NOT to refactor, even if it looks tempting",
            "Clarify test expectations — unit? integration? both?",
            "Set boundaries around dependency changes",
        ],
    ),
    "inputs": SectionGuidance(
        hint="Specs, interfaces, tests to pass, reference implementations.",
        placeholder=(
            "- Interface: tasks/base.py (TaskBase class)\n"
            "- Tests to pass: tests/test_executor.py\n"
            "- Pattern ref: infra/logging.py"
        ),
        tips=[
            "Provide the interface the code must implement",
            "Include test files — even if empty, the structure helps",
            "Reference pattern files the implementation should follow",
        ],
    ),
    "outputs": SectionGuidance(
        hint="The files, tests, and docs you expect to receive.",
        placeholder=(
            "orchestrator/executor.py, tests/test_executor.py (>90% coverage), "
            "README section, inline docstrings"
        ),
        tips=[
            "Name specific files and their expected locations",
            "State coverage expectations",
            "Specify documentation requirements",
        ],
    ),
    "constraint": SectionGuidance(
        hint="Rules the implementation must follow. No exceptions.",
        placeholder=(
            "Python 3.11+. async/await only. Type hints + docstrings on all "
            "public methods. Tests pass in CI. Follow /orchestrator patterns."
        ),
        tips=[
            "Be explicit about language version and style",
            "State the testing requirements clearly",
            "Reference the CI pipeline if it matters",
        ],
    ),
    "attention": SectionGuidance(
        hint="Traps, gotchas, and edge cases the implementer must handle.",
        placeholder=(
            "asyncio.gather swallows exceptions — use return_exceptions=True. "
            "Task cleanup() is optional but MUST be called on failure. "
            "Propagate correlation_id through async contexts."
        ),
        tips=[
            "Name the function, the parameter, the edge case",
            "Include examples of what wrong behaviour looks like",
            "Mention things that pass tests but fail in production",
        ],
    ),
}
