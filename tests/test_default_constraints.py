"""Tests for per-task-type default constraints (single source of truth)."""

import pytest

from greenlit.guidance import get_default_constraints
from greenlit.sections import TASK_TYPES

BUILTIN_TYPES = list(TASK_TYPES.keys())

EXPECTED = {
    "review": [
        "Read-only: do not create, modify, or commit any files.",
        "Report findings, do not fix them.",
        "Every finding must reference a file and line.",
    ],
    "plan": [
        "Do not implement anything — the plan is the only output.",
        "Surface assumptions and open questions explicitly rather than resolving them silently.",
    ],
    "action": [
        "Change nothing outside SCOPE.",
        "Do not add or upgrade dependencies without flagging first.",
        "If a DONE criterion cannot be met, stop and report — never redefine done.",
    ],
    "debug": [
        "Reproduce the failure before changing anything.",
        "Fix the root cause with the smallest change; no opportunistic refactoring.",
        "Never modify or delete tests to make them pass.",
    ],
    "research": [
        "Do not modify the codebase.",
        "Distinguish verified fact from inference.",
        "Cite sources for external claims.",
    ],
}


@pytest.mark.parametrize("task_type,expected", EXPECTED.items())
def test_default_constraints_exact(task_type, expected):
    assert get_default_constraints(task_type) == expected


@pytest.mark.parametrize("task_type", BUILTIN_TYPES)
def test_cap_of_three(task_type):
    constraints = get_default_constraints(task_type)
    assert len(constraints) <= 3, (
        f"{task_type!r} has {len(constraints)} defaults — the hard cap is 3."
    )


@pytest.mark.parametrize("task_type", BUILTIN_TYPES)
def test_every_default_is_nonempty(task_type):
    for c in get_default_constraints(task_type):
        assert c.strip(), f"{task_type!r} has a blank default constraint"


def test_accessor_returns_a_copy():
    a = get_default_constraints("action")
    a.append("mutated")
    assert "mutated" not in get_default_constraints("action")


def test_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown task type"):
        get_default_constraints("nonexistent")
