from __future__ import annotations

import warnings

from rich_click.rich_command import RichGroup


warnings.warn(
    "RichCommand is moving from rich_click.rich_group to rich_click.rich_command in a future version.",
    DeprecationWarning,
    stacklevel=2,
)


__all__ = ["RichGroup"]
