"""Section definitions and task type registry."""

from dataclasses import dataclass

TASK_TYPES = {
    "review": {
        "label": "Review",
        "short": "r",
        "desc": "Code review, PR review, architecture review",
    },
    "plan": {
        "label": "Plan",
        "short": "p",
        "desc": "Architecture, design, task breakdown",
    },
    "action": {
        "label": "Action",
        "short": "a",
        "desc": "Implementation, refactoring, migration",
    },
    "debug": {
        "label": "Debug",
        "short": "d",
        "desc": "Diagnose failures, trace bugs, root cause analysis",
    },
    "research": {
        "label": "Research",
        "short": "rs",
        "desc": "Spikes, investigations, trade-off analysis",
    },
}


@dataclass
class SectionGuidance:
    hint: str
    placeholder: str
    tips: list[str]


@dataclass
class Section:
    key: str
    label: str
    tagline: str
    default: str = ""


SECTIONS: list[Section] = [
    Section(key="ask", label="ASK", tagline="What exactly do you want done?"),
    Section(
        key="goal",
        label="GOAL",
        tagline="Why are you doing this? What does success look like?",
    ),
    Section(
        key="context",
        label="CONTEXT",
        tagline="Background the agent needs to do good work.",
    ),
    Section(
        key="scope", label="SCOPE", tagline="Hard boundaries. What's in, what's out."
    ),
    Section(
        key="delegation",
        label="DELEGATION",
        tagline="Agent roles for sub-tasks. Who does what.",
    ),
    Section(key="inputs", label="INPUTS", tagline="What material is being provided?"),
    Section(
        key="outputs",
        label="OUTPUTS",
        tagline="What deliverables do you expect back?",
    ),
    Section(
        key="constraint",
        label="CONSTRAINT",
        tagline="Hard rules. Non-negotiable requirements.",
    ),
    Section(
        key="attention",
        label="ATTENTION",
        tagline="Red flags. Edge cases. Things that look fine but aren't.",
        default=(
            "- Restate the ask in one line for user inspection before starting.\n"
            "- If any clarification questions exist, ask them before starting work."
        ),
    ),
]


def get_sections() -> list[Section]:
    return SECTIONS
