# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Read and write strategies for Airbyte."""

from __future__ import annotations

from enum import Enum

from airbyte_cdk.models import DestinationSyncMode


_MERGE = "merge"
_REPLACE = "replace"
_APPEND = "append"
_AUTO = "auto"


class WriteStrategy(str, Enum):
    """Read strategies for Airbyte.

    Read strategies set a preferred method for writing data to a destination. The actual method used
    may differ based on the capabilities of the destination.

    If a destination does not support the preferred method, it will fall back to the next best
    method.
    """

    MERGE = _MERGE
    """Merge new records with existing records.

    This requires a primary key to be set on the stream.
    If no primary key is set, this will raise an exception.

    To apply this strategy in cases where some destination streams don't have a primary key,
    please use the `auto` strategy instead.
    """

    APPEND = _APPEND
    """Append new records to existing records."""

    REPLACE = _REPLACE
    """Replace existing records with new records."""

    AUTO = _AUTO
    """Automatically determine the best strategy to use.

    This will use the following logic:
    - If there's a primary key, use merge.
    - Else, if there's an incremental key, use append.
    - Else, use full replace (table swap).
    """


class WriteMethod(str, Enum):
    """Write methods for Airbyte.

    Unlike write strategies, write methods are expected to be fully resolved and do not require any
    additional logic to determine the best method to use.

    If a destination does not support the declared method, it will raise an exception.
    """

    MERGE = _MERGE
    """Merge new records with existing records.

    This requires a primary key to be set on the stream.
    If no primary key is set, this will raise an exception.

    To apply this strategy in cases where some destination streams don't have a primary key,
    please use the `auto` strategy instead.
    """

    APPEND = _APPEND
    """Append new records to existing records."""

    REPLACE = _REPLACE
    """Replace existing records with new records."""

    @property
    def destination_sync_mode(self) -> DestinationSyncMode:
        """Convert the write method to a destination sync mode."""
        if self == WriteMethod.MERGE:
            return DestinationSyncMode.append_dedup

        if self == WriteMethod.APPEND:
            return DestinationSyncMode.append

        if self == WriteMethod.REPLACE:
            return DestinationSyncMode.overwrite

        msg = f"Unknown write method: {self}"  # type: ignore [unreachable]
        raise ValueError(msg)
