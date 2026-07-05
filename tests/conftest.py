"""Shared pytest fixtures."""

import pytest
from rich.console import Console


@pytest.fixture(autouse=True)
def reset_display_console():
    """Restore stdout console between tests that use --stdout / use_stderr()."""
    import greenlit.cli as _cli
    import greenlit.display as _display
    original = Console()
    yield
    _display.console = original
    _cli.console = original
