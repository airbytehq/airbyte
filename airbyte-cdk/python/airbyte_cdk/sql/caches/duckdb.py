# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""A DuckDB implementation of the Airbyte cache.

## Usage Example

```python
from airbyte as ab
from airbyte.caches import DuckDBCache

cache = DuckDBCache(
    db_path="/path/to/my/duckdb-file",
    schema_name="myschema",
)
```
"""

from __future__ import annotations

import warnings

from duckdb_engine import DuckDBEngineWarning
from pydantic import PrivateAttr

from airbyte_cdk.sql.duckdb import DuckDBConfig, DuckDBSqlProcessor
from airbyte_cdk.sql.caches.base import CacheBase


# Suppress warnings from DuckDB about reflection on indices.
# https://github.com/Mause/duckdb_engine/issues/905
warnings.filterwarnings(
    "ignore",
    message="duckdb-engine doesn't yet support reflection on indices",
    category=DuckDBEngineWarning,
)


class DuckDBCache(DuckDBConfig, CacheBase):
    """A DuckDB cache."""

    _sql_processor_class: type[DuckDBSqlProcessor] = PrivateAttr(default=DuckDBSqlProcessor)


# Expose the Cache class and also the Config class.
__all__ = [
    "DuckDBCache",
    "DuckDBConfig",
]
