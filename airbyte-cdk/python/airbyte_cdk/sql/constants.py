# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Constants shared across the PyAirbyte codebase."""

from __future__ import annotations

import os
from pathlib import Path


DEBUG_MODE = False  # Set to True to enable additional debug logging.


AB_EXTRACTED_AT_COLUMN = "_airbyte_extracted_at"
"""A column that stores the timestamp when the record was extracted."""

AB_META_COLUMN = "_airbyte_meta"
"""A column that stores metadata about the record."""

AB_RAW_ID_COLUMN = "_airbyte_raw_id"
"""A column that stores a unique identifier for each row in the source data.

Note: The interpretation of this column is slightly different from in Airbyte Dv2 destinations.
In Airbyte Dv2 destinations, this column points to a row in a separate 'raw' table. In PyAirbyte,
this column is simply used as a unique identifier for each record as it is received.

PyAirbyte uses ULIDs for this column, which are identifiers that can be sorted by time
received. This allows us to determine the debug the order of records as they are received, even if
the source provides records that are tied or received out of order from the perspective of their
`emitted_at` (`_airbyte_extracted_at`) timestamps.
"""

AB_INTERNAL_COLUMNS = {
    AB_RAW_ID_COLUMN,
    AB_EXTRACTED_AT_COLUMN,
    AB_META_COLUMN,
}
"""A set of internal columns that are reserved for PyAirbyte's internal use."""

DEFAULT_CACHE_SCHEMA_NAME = "airbyte_raw"
"""The default schema name to use for caches.

Specific caches may override this value with a different schema name.
"""

DEFAULT_CACHE_ROOT: Path = (
    Path() / ".cache"
    if "AIRBYTE_CACHE_ROOT" not in os.environ
    else Path(os.environ["AIRBYTE_CACHE_ROOT"])
)
"""Default cache root is `.cache` in the current working directory.

The default location can be overridden by setting the `AIRBYTE_CACHE_ROOT` environment variable.

Overriding this can be useful if you always want to store cache files in a specific location.
For example, in ephemeral environments like Google Colab, you might want to store cache files in
your mounted Google Drive by setting this to a path like `/content/drive/MyDrive/Airbyte/cache`.
"""

DEFAULT_ARROW_MAX_CHUNK_SIZE = 100_000
"""The default number of records to include in each batch of an Arrow dataset."""


def _str_to_bool(value: str) -> bool:
    """Convert a string value of an environment values to a boolean value."""
    return bool(value) and value.lower() not in {"", "0", "false", "f", "no", "n", "off"}


TEMP_DIR_OVERRIDE: Path | None = (
    Path(os.environ["AIRBYTE_TEMP_DIR"]) if os.getenv("AIRBYTE_TEMP_DIR") else None
)
"""The directory to use for temporary files.

This value is read from the `AIRBYTE_TEMP_DIR` environment variable. If the variable is not set,
Tempfile will use the system's default temporary directory.

This can be useful if you want to store temporary files in a specific location (or) when you
need your temporary files to exist in user level directories, and not in system level
directories for permissions reasons.
"""

TEMP_FILE_CLEANUP = _str_to_bool(
    os.getenv(
        key="AIRBYTE_TEMP_FILE_CLEANUP",
        default="true",
    )
)
"""Whether to clean up temporary files after use.

This value is read from the `AIRBYTE_TEMP_FILE_CLEANUP` environment variable. If the variable is
not set, the default value is `True`.
"""
