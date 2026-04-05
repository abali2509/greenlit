"""Template loading tests — T16."""

import sys
import textwrap
from unittest import mock

import pytest

from greenlit.sections import SECTIONS

SECTION_KEYS = [s.key for s in SECTIONS]


def _write_yaml(tmp_path, content: str, filename: str = "template.yaml"):
    p = tmp_path / filename
    p.write_text(textwrap.dedent(content))
    return str(p)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_valid_template_loads(tmp_path):
    path = _write_yaml(tmp_path, """\
        name: dbt_review
        label: dbt Review
        icon: "custom"
        description: Review dbt models
        extends: review
        sections:
          ask:
            hint: "Which models?"
            placeholder: "Review staging models..."
            tips:
              - "Reference the specific model paths"
    """)
    from greenlit.templates import load_template
    name, meta, sections = load_template(path)
    assert name == "dbt_review"
    assert meta["label"] == "dbt Review"
    assert meta["icon"] == "custom"
    assert meta["desc"] == "Review dbt models"
    assert sections is SECTIONS


def test_template_returns_guidance_dict(tmp_path):
    path = _write_yaml(tmp_path, """\
        name: custom
        label: Custom
        extends: action
        sections: {}
    """)
    from greenlit.templates import load_template
    _, meta, _ = load_template(path)
    guidance = meta["_guidance"]
    assert set(guidance.keys()) == set(SECTION_KEYS)


def test_template_overrides_ask_hint(tmp_path):
    path = _write_yaml(tmp_path, """\
        name: custom
        label: Custom
        extends: review
        sections:
          ask:
            hint: "My custom hint"
    """)
    from greenlit.templates import load_template
    _, meta, _ = load_template(path)
    assert meta["_guidance"]["ask"].hint == "My custom hint"


# ---------------------------------------------------------------------------
# Fallback to base type for unspecified sections
# ---------------------------------------------------------------------------

def test_unspecified_sections_inherit_from_base(tmp_path):
    from greenlit.guidance import get_guidance
    from greenlit.templates import load_template

    path = _write_yaml(tmp_path, """\
        name: custom
        label: Custom
        extends: plan
        sections:
          ask:
            hint: "Override only ask"
    """)
    _, meta, _ = load_template(path)
    base = get_guidance("plan")

    # goal should match base plan guidance exactly
    assert meta["_guidance"]["goal"].hint == base["goal"].hint
    assert meta["_guidance"]["goal"].placeholder == base["goal"].placeholder


def test_extends_defaults_to_action_when_omitted(tmp_path):
    from greenlit.guidance import get_guidance
    from greenlit.templates import load_template

    path = _write_yaml(tmp_path, """\
        name: minimal
        label: Minimal
    """)
    _, meta, _ = load_template(path)
    base = get_guidance("action")
    assert meta["_guidance"]["ask"].hint == base["ask"].hint


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_missing_name_raises_value_error(tmp_path):
    from greenlit.templates import load_template

    path = _write_yaml(tmp_path, """\
        label: No Name
        extends: action
    """)
    with pytest.raises(ValueError, match="missing required field.*name"):
        load_template(path)


def test_missing_label_raises_value_error(tmp_path):
    from greenlit.templates import load_template

    path = _write_yaml(tmp_path, """\
        name: no_label
        extends: action
    """)
    with pytest.raises(ValueError, match="missing required field.*label"):
        load_template(path)


def test_nonexistent_file_raises_file_not_found(tmp_path):
    from greenlit.templates import load_template

    with pytest.raises(FileNotFoundError):
        load_template(str(tmp_path / "does_not_exist.yaml"))


def test_malformed_yaml_raises_value_error(tmp_path):
    from greenlit.templates import load_template

    path = tmp_path / "bad.yaml"
    path.write_text("key: [unclosed bracket")
    with pytest.raises(ValueError, match="Malformed YAML"):
        load_template(path)


def test_non_mapping_yaml_raises_value_error(tmp_path):
    from greenlit.templates import load_template

    path = _write_yaml(tmp_path, "- item1\n- item2\n")
    with pytest.raises(ValueError, match="must be a YAML mapping"):
        load_template(path)


def test_unknown_extends_raises_value_error(tmp_path):
    from greenlit.templates import load_template

    path = _write_yaml(tmp_path, """\
        name: custom
        label: Custom
        extends: nonexistent_base_type
    """)
    with pytest.raises(ValueError, match="unknown task type"):
        load_template(path)


def test_missing_pyyaml_raises_import_error(tmp_path):
    path = _write_yaml(tmp_path, "name: x\nlabel: X\n")
    with mock.patch.dict(sys.modules, {"yaml": None}):
        from importlib import reload

        import greenlit.templates as tpl_module
        reload(tpl_module)
        with pytest.raises(ImportError, match="pip install greenlit\\[templates\\]"):
            tpl_module.load_template(path)
    # reload back to real state
    import importlib
    importlib.reload(tpl_module)
