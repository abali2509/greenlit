"""Per-task-type guidance registry."""

from greenlit.sections import SectionGuidance

_REGISTRY: dict[str, str] = {
    "review": "greenlit.guidance.review",
    "plan": "greenlit.guidance.plan",
    "action": "greenlit.guidance.action",
    "debug": "greenlit.guidance.debug",
    "research": "greenlit.guidance.research",
}

# Custom task types registered at runtime via register_guidance()
_CUSTOM: dict[str, dict[str, SectionGuidance]] = {}


def register_guidance(task_type: str, guidance: dict[str, SectionGuidance]) -> None:
    """Register a custom task type's guidance (used by template loading)."""
    _CUSTOM[task_type] = guidance


def get_guidance(task_type: str) -> dict[str, SectionGuidance]:
    if task_type in _CUSTOM:
        return _CUSTOM[task_type]
    if task_type not in _REGISTRY:
        raise ValueError(f"Unknown task type {task_type!r}. Available: {', '.join(_REGISTRY)}")
    import importlib
    module = importlib.import_module(_REGISTRY[task_type])
    return module.GUIDANCE
