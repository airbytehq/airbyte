# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Constants shared across the Airbyte codebase."""

from __future__ import annotations

DEBUG_MODE = False  # Set to True to enable additional debug logging.

AB_EXTRACTED_AT_COLUMN = "_airbyte_extracted_at"
"""A column that stores the timestamp when the record was extracted."""

AB_META_COLUMN = "_airbyte_meta"
"""A column that stores metadata about the record."""

AB_RAW_ID_COLUMN = "_airbyte_raw_id"
"""A column that stores a unique identifier for each row in the source data.

Note: The interpretation of this column is slightly different from in Airbyte Dv2 destinations.
In Airbyte Dv2 destinations, this column points to a row in a separate 'raw' table. In Airbyte,
this column is simply used as a unique identifier for each record as it is received.

Airbyte uses ULIDs for this column, which are identifiers that can be sorted by time
received. This allows us to determine the debug the order of records as they are received, even if
the source provides records that are tied or received out of order from the perspective of their
`emitted_at` (`_airbyte_extracted_at`) timestamps.
"""

AB_INTERNAL_COLUMNS = {
    AB_RAW_ID_COLUMN,
    AB_EXTRACTED_AT_COLUMN,
    AB_META_COLUMN,
}
"""A set of internal columns that are reserved for Airbyte's internal use."""
