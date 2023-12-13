"""A SQL implementation of the cache."""

from .base import FileCacheBase
from pathlib import Path


class SqlCache(FileCacheBase):
    """A SQL implementation of the cache.

    A file cache is used to store the data in parquet files.
    """

    def __init__(
        self,
        cache_path: Path,  # Path to directory where parquet files will be stored
        sql_engine: str,  # SQL engine to use
        **kwargs,  # Additional arguments to pass to the base class (future proofing)
    ):
        self.cache_path = cache_path
        super().__init__(**kwargs)
