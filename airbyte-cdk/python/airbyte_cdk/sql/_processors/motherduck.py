# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""A MotherDuck implementation of the cache, built on DuckDB.

## Usage Example

```python
from airbyte as ab
from airbyte.caches import MotherDuckCache

cache = MotherDuckCache(
    database="mydatabase",
    schema_name="myschema",
    api_key=ab.get_secret("MOTHERDUCK_API_KEY"),
)
"""

from __future__ import annotations

import warnings

from airbyte_cdk.sql._processors.duckdb import DuckDBConfig, DuckDBSqlProcessor
from airbyte_cdk.sql.secrets import SecretString
from duckdb_engine import DuckDBEngineWarning
from overrides import overrides
from pydantic import Field

# Suppress warnings from DuckDB about reflection on indices.
# https://github.com/Mause/duckdb_engine/issues/905
warnings.filterwarnings(
    "ignore",
    message="duckdb-engine doesn't yet support reflection on indices",
    category=DuckDBEngineWarning,
)


class MotherDuckConfig(DuckDBConfig):
    """Configuration for the MotherDuck cache."""

    database: str = Field()
    api_key: SecretString = Field()
    db_path: str = Field(default="md:")
    custom_user_agent: str = Field(default="airbyte")

    @overrides
    def get_sql_alchemy_url(self) -> SecretString:
        """Return the SQLAlchemy URL to use."""
        # Suppress warnings from DuckDB about reflection on indices.
        # https://github.com/Mause/duckdb_engine/issues/905
        warnings.filterwarnings(
            "ignore",
            message="duckdb-engine doesn't yet support reflection on indices",
            category=DuckDBEngineWarning,
        )

        return SecretString(
            f"duckdb:///md:{self.database}?motherduck_token={self.api_key}"
            f"&custom_user_agent={self.custom_user_agent}"
            # Not sure why this doesn't work. We have to override later in the flow.
            # f"&schema={self.schema_name}"
        )

    @overrides
    def get_database_name(self) -> str:
        """Return the name of the database."""
        return self.database


class MotherDuckSqlProcessor(DuckDBSqlProcessor):
    """A cache implementation for MotherDuck."""

    supports_merge_insert = False

    @overrides
    def _setup(self) -> None:
        """Do any necessary setup, if applicable.

        Note: The DuckDB parent class requires pre-creation of local directory structure. We
        don't need to do that here so we override the method be a no-op.
        """
        # No setup to do and no need to pre-create local file storage.
        pass
