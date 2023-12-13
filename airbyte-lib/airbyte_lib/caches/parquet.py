"""A Parquet cache implementation."""

from pathlib import Path
import pyarrow as pa
import ulid

from airbyte_lib.bases import CacheConfigBase, FileCacheBase


class ParquetCacheConfig(CacheConfigBase):
    """Configuration for the Snowflake cache."""

    type: str = "parquet"
    cache_path: str


class ParquetCache(FileCacheBase):
    """A Parquet cache implementation."""

    def __init__(
        self,
        cache_path: Path,  # Path to directory where parquet files will be stored
        **kwargs,  # Additional arguments to pass to the base class (future proofing)
    ):
        self.cache_path = cache_path
        super().__init__(**kwargs)

    def get_new_cache_file_path(
        self,
        stream_name: str,
        batch_id: str | None = None,  # ULID of the batch
    ) -> Path:
        """Return a new cache file path for the given stream."""
        batch_id = batch_id or ulid.new().str
        return self.cache_path / f"{stream_name}_{batch_id}.parquet"

    def write_batch_to_file(
        self,
        stream_name: str,
        record_batch: pa.Table | pa.RecordBatch,
    ) -> Path:
        """
        Process a record batch.

        Return the path to the cache file.
        """
        output_file_path = self.get_new_cache_file_path(stream_name)
        with pa.parquet.ParquetWriter(output_file_path, record_batch.schema) as writer:
            writer.write_table(record_batch)

        return output_file_path
