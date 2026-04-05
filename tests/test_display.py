"""Unit tests for display.py — _strip_hint_block and show_task_selector short-key resolution."""

from unittest.mock import patch

from greenlit.display import _strip_hint_block, show_task_selector

# ── _strip_hint_block ─────────────────────────────────────────────────────────

class TestStripHintBlock:
    def test_strips_hint_block_from_content(self):
        text = "<!-- greenlit-hint\nSome hint text\n-->\n\nActual content"
        assert _strip_hint_block(text) == "Actual content"

    def test_strips_hint_block_with_tips(self):
        text = "<!-- greenlit-hint\nHint\n\n→ tip one\n→ tip two\n-->\n\nReal stuff"
        assert _strip_hint_block(text) == "Real stuff"

    def test_preserves_content_without_hint_block(self):
        text = "Just some plain content\nwith multiple lines"
        assert _strip_hint_block(text) == text

    def test_empty_string(self):
        assert _strip_hint_block("") == ""

    def test_only_hint_block_returns_empty(self):
        text = "<!-- greenlit-hint\nHint here\n-->"
        assert _strip_hint_block(text) == ""

    def test_content_before_and_after_hint_block(self):
        text = "before\n<!-- greenlit-hint\nhint\n-->\nafter"
        result = _strip_hint_block(text)
        assert "before" in result
        assert "after" in result
        assert "hint" not in result


# ── show_task_selector short-key resolution ───────────────────────────────────

TASK_TYPES = {
    "review": {"label": "Review", "short": "r", "desc": "Code review"},
    "plan": {"label": "Plan", "short": "p", "desc": "Design"},
    "action": {"label": "Action", "short": "a", "desc": "Implementation"},
}


class TestShowTaskSelector:
    def test_short_key_resolves_to_full_type(self):
        with patch("greenlit.display.Prompt.ask", return_value="r"), \
             patch("greenlit.display.console.print"):
            result = show_task_selector(TASK_TYPES)
        assert result == "review"

    def test_full_key_passthrough(self):
        with patch("greenlit.display.Prompt.ask", return_value="action"), \
             patch("greenlit.display.console.print"):
            result = show_task_selector(TASK_TYPES)
        assert result == "action"

    def test_each_short_key_maps_correctly(self):
        expected = {"r": "review", "p": "plan", "a": "action"}
        for short, full in expected.items():
            with patch("greenlit.display.Prompt.ask", return_value=short), \
                 patch("greenlit.display.console.print"):
                result = show_task_selector(TASK_TYPES)
            assert result == full, f"Expected {short!r} → {full!r}, got {result!r}"
