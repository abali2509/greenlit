"""Tests for the bundled skill files' handling of default constraints.

greenlit-Write (skill_write.md) must embed the per-type defaults verbatim and
restate design rule 1. greenlit-Read (skill.md) must stay execution-only — no
constraint-seeding text may leak into it (constraints live in the spec, never
applied out-of-band by the read/execute skill).
"""

import importlib.resources

from greenlit.guidance import get_default_constraints
from greenlit.sections import TASK_TYPES


def _skill(name: str) -> str:
    return importlib.resources.files("greenlit.skills").joinpath(name).read_text()


class TestGreenlitWriteEmbedsDefaults:
    def test_every_type_default_appears_verbatim(self):
        text = _skill("skill_write.md")
        for task_type in TASK_TYPES:
            for constraint in get_default_constraints(task_type):
                assert constraint in text, (
                    f"skill_write.md missing {task_type} default: {constraint!r}"
                )

    def test_restates_design_rule_1(self):
        low = _skill("skill_write.md").lower()
        assert "out-of-band" in low
        assert "complete contract" in low

    def test_instructs_verbatim_inclusion(self):
        assert "verbatim" in _skill("skill_write.md").lower()


class TestGreenlitReadUntouched:
    def test_no_default_constraint_text_leaks_into_read_skill(self):
        text = _skill("skill.md")
        for task_type in TASK_TYPES:
            for constraint in get_default_constraints(task_type):
                assert constraint not in text, (
                    f"skill.md (greenlit-Read) must not carry seeding text; "
                    f"found {task_type} default: {constraint!r}"
                )
