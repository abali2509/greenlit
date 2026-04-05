"""Section and guidance validation tests — T15."""

import pytest

from greenlit.guidance import get_guidance
from greenlit.sections import SECTIONS, TASK_TYPES, get_sections

SECTION_KEYS = [s.key for s in SECTIONS]
BUILTIN_TYPES = list(TASK_TYPES.keys())


def test_no_duplicate_section_keys():
    assert len(SECTION_KEYS) == len(set(SECTION_KEYS))


def test_get_sections_returns_all_sections():
    assert get_sections() == SECTIONS


def test_all_sections_have_nonempty_labels():
    for s in SECTIONS:
        assert s.label.strip(), f"Section {s.key!r} has empty label"


def test_all_sections_have_nonempty_taglines():
    for s in SECTIONS:
        assert s.tagline.strip(), f"Section {s.key!r} has empty tagline"


@pytest.mark.parametrize("task_type", BUILTIN_TYPES)
def test_guidance_covers_all_sections(task_type):
    guidance = get_guidance(task_type)
    missing = [key for key in SECTION_KEYS if key not in guidance]
    assert not missing, f"{task_type!r} missing guidance for: {missing}"


@pytest.mark.parametrize("task_type", BUILTIN_TYPES)
def test_guidance_hints_nonempty(task_type):
    guidance = get_guidance(task_type)
    for key in SECTION_KEYS:
        g = guidance[key]
        assert g.hint.strip(), f"{task_type!r}/{key}: hint is empty"


@pytest.mark.parametrize("task_type", BUILTIN_TYPES)
def test_guidance_placeholders_nonempty(task_type):
    guidance = get_guidance(task_type)
    for key in SECTION_KEYS:
        g = guidance[key]
        assert g.placeholder.strip(), f"{task_type!r}/{key}: placeholder is empty"


@pytest.mark.parametrize("task_type", BUILTIN_TYPES)
def test_guidance_tips_nonempty(task_type):
    guidance = get_guidance(task_type)
    for key in SECTION_KEYS:
        g = guidance[key]
        assert g.tips, f"{task_type!r}/{key}: tips list is empty"
        for tip in g.tips:
            assert tip.strip(), f"{task_type!r}/{key}: has blank tip string"


def test_get_guidance_raises_for_unknown_type():
    with pytest.raises(ValueError, match="Unknown task type"):
        get_guidance("nonexistent_task_type_xyz")


def test_task_types_have_required_fields():
    for name, meta in TASK_TYPES.items():
        assert "label" in meta, f"{name!r} missing 'label'"
        assert "desc" in meta, f"{name!r} missing 'desc'"
