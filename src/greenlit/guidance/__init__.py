"""Per-task-type guidance registry."""

_REGISTRY: dict[str, str] = {
    "review": "greenlit.guidance.review",
    "plan": "greenlit.guidance.plan",
    "action": "greenlit.guidance.action",
    "debug": "greenlit.guidance.debug",
    "research": "greenlit.guidance.research",
}


def _load_module(task_type: str):
    if task_type not in _REGISTRY:
        raise ValueError(f"Unknown task type {task_type!r}. Available: {', '.join(_REGISTRY)}")
    import importlib
    return importlib.import_module(_REGISTRY[task_type])


def get_guidance(task_type: str) -> dict:
    return _load_module(task_type).GUIDANCE


def get_default_constraints(task_type: str) -> list[str]:
    """Return the task type's default CONSTRAINT lines (single source of truth).

    Every authoring path that seeds default constraints must call this — the text
    lives only in the guidance modules, nowhere else in the codebase.
    """
    return list(getattr(_load_module(task_type), "DEFAULT_CONSTRAINTS", []))
