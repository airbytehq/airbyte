# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Internal utility functions for dealing with text."""
from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Iterable


def lower_case_set(str_iter: Iterable[str]) -> set[str]:
    """Converts a list of strings to a set of lower case strings."""
    return {s.lower() for s in str_iter}
