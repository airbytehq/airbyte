# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Internal helper functions for working with temporary files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from airbyte._util.meta import is_windows


if TYPE_CHECKING:
    from pathlib import Path


def get_bin_dir(venv_path: Path, /) -> Path:
    """Get the directory where executables are installed."""
    if is_windows():
        return venv_path / "Scripts"

    return venv_path / "bin"
