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

from duckdb_engine import DuckDBEngineWarning
from overrides import overrides
from pydantic import Field
from sqlalchemy import Engine, create_engine

from airbyte_cdk.sql.constants import DEBUG_MODE
from airbyte_cdk.sql.secrets import SecretString
from destination_motherduck.processors.duckdb import DuckDBConfig, DuckDBSqlProcessor


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

        # We defer adding schema name and API token until `create_engine()` call.
        return SecretString(f"duckdb:///md:{self.database}?custom_user_agent={self.custom_user_agent}")

    @overrides
    def get_database_name(self) -> str:
        """Return the name of the database."""
        return self.database

    @overrides
    def get_sql_engine(self) -> Engine:
        """
        Return a new SQL engine to use.

        This method is overridden to:
            - ensure that the database parent directory is created if it doesn't exist.
            - pass the DuckDB query parameters (such as motherduck_token) via the config
        """
        return create_engine(
            url=self.get_sql_alchemy_url(),
            echo=DEBUG_MODE,
            execution_options={
                "schema_translate_map": {None: self.schema_name},
            },
            future=True,
            connect_args={
                "config": {
                    "motherduck_token": self.api_key,
                },
            },
        )


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
