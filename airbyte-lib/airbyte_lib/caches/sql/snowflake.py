"""A Snowflake implementation of the cache."""

from __future__ import annotations


from .base import SQLCache

from airbyte_lib.parquet import ParquetCache, ParquetCacheConfig
from overrides import overrides


class SnowflakeCacheConfig(ParquetCacheConfig):
    """Configuration for the Snowflake cache.

    Also inherits config from the ParquetCache, which is responsible for writing files to disk.
    """

    type: str = "snowflake"
    account: str
    username: str
    password: str
    warehouse: str
    database: str
    schema: str

    @overrides
    def get_sql_alchemy_url(self) -> str:
        """Return the SQL alchemy URL to use."""
        return (
            f"snowflake://{self.username}:{self.password}@{self.account}/"
            f"?warehouse={self.warehouse}&database={self.database}&schema={self.schema}"
        )


class SnowflakeSQLCache(SQLCache, ParquetCache):
    """A Snowflake implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    """

    def __init__(
        self,
        config: SnowflakeCacheConfig,
        **kwargs,  # Additional arguments to pass to the base class (future proofing)
    ):
        super().__init__(
            config=config,
            **kwargs,
        )
