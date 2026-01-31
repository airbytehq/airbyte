# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Write strategy enum for SQL destinations."""

from __future__ import annotations

import enum


class WriteStrategy(enum.Enum):
    """Write strategy for SQL destinations."""
    AUTO = "auto"
    APPEND = "append"
    REPLACE = "replace"
    MERGE = "merge"
