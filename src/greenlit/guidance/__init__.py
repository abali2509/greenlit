"""Per-task-type guidance registry."""

_REGISTRY: dict[str, str] = {
    "review": "greenlit.guidance.review",
    "plan": "greenlit.guidance.plan",
    "action": "greenlit.guidance.action",
    "debug": "greenlit.guidance.debug",
    "research": "greenlit.guidance.research",
}


def get_guidance(task_type: str) -> dict:
    if task_type not in _REGISTRY:
        raise ValueError(f"Unknown task type {task_type!r}. Available: {', '.join(_REGISTRY)}")
    import importlib
    module = importlib.import_module(_REGISTRY[task_type])
    return module.GUIDANCE
