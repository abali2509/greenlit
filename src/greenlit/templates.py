"""YAML template loading for custom task types."""

from __future__ import annotations

from pathlib import Path

from greenlit.guidance import get_guidance
from greenlit.sections import Section, SectionGuidance, get_sections


def load_template(path: str) -> tuple[dict, list[Section]]:
    """Load a YAML template file and return (task_type_meta, sections).

    The task_type_meta dict has keys: name, label, icon (optional), description.
    Sections not defined in the YAML fall back to the base type specified by `extends`.

    Raises:
        FileNotFoundError: if the path does not exist.
        ValueError: if the YAML is missing required fields or malformed.
        ImportError: if pyyaml is not installed.
    """
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "pyyaml is required for template loading. "
            "Install it with: pip install greenlit[templates]"
        )

    template_path = Path(path)
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {path}")

    try:
        with open(template_path) as f:
            raw = yaml.safe_load(f)
    except Exception as exc:
        raise ValueError(f"Malformed YAML in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError(f"Template must be a YAML mapping, got {type(raw).__name__}")

    for required in ("name", "label"):
        if required not in raw:
            raise ValueError(f"Template missing required field: {required!r}")

    base_type = raw.get("extends", "action")
    try:
        base_guidance = get_guidance(base_type)
    except ValueError as exc:
        raise ValueError(f"Template 'extends' refers to unknown task type {base_type!r}") from exc

    section_overrides: dict = raw.get("sections", {}) or {}
    sections = get_sections()

    # Merge YAML overrides on top of base guidance — stored back on a fresh Section list
    # We rebuild guidance lookups per section using a patched guidance dict.
    # Callers retrieve guidance via get_guidance; templates register a custom type.
    merged_guidance: dict[str, SectionGuidance] = {}
    for section in sections:
        base_g = base_guidance.get(section.key, SectionGuidance(hint="", placeholder="", tips=[]))
        override = section_overrides.get(section.key, {}) or {}
        merged_guidance[section.key] = SectionGuidance(
            hint=override.get("hint", base_g.hint),
            placeholder=override.get("placeholder", base_g.placeholder),
            tips=list(override.get("tips", base_g.tips)),
        )

    task_type_meta = {
        "label": raw["label"],
        "desc": raw.get("description", ""),
        "icon": raw.get("icon", ""),
        "_guidance": merged_guidance,
    }

    return raw["name"], task_type_meta, sections
