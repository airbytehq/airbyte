# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Read and write strategies for AirbyteLib."""
from __future__ import annotations

from enum import Enum


class WriteStrategy(str, Enum):
    """Read strategies for AirbyteLib."""

    MERGE = "merge"
    """Merge new records with existing records.

    This requires a primary key to be set on the stream.
    If no primary key is set, this will raise an exception.

    To apply this strategy in cases where some destination streams don't have a primary key,
    please use the `auto` strategy instead.
    """

    APPEND = "append"
    """Append new records to existing records."""

    REPLACE = "replace"
    """Replace existing records with new records."""

    AUTO = "auto"
    """Automatically determine the best strategy to use.

    This will use the following logic:
    - If there's a primary key, use merge.
    - Else, if there's an incremental key, use append.
    - Else, use full replace (table swap).
    """
