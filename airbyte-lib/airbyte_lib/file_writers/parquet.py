"""A Parquet cache implementation."""

from pathlib import Path
from typing import cast
import pyarrow as pa
import ulid

from .base import FileWriterBase, FileWriterConfigBase
from overrides import overrides


class ParquetWriterConfig(FileWriterConfigBase):
    """Configuration for the Snowflake cache."""

    type: str = "parquet"

    # Inherits from base class:
    # cache_path: str

class ParquetWriter(FileWriterBase):
    """A Parquet cache implementation."""

    config_class = ParquetWriterConfig

    def get_new_cache_file_path(
        self,
        stream_name: str,
        batch_id: str | None = None,  # ULID of the batch
    ) -> Path:
        """Return a new cache file path for the given stream."""
        batch_id = batch_id or str(ulid.ULID())
        config: ParquetWriterConfig = cast(ParquetWriterConfig, self.config)
        return Path(config.cache_path) / f"{stream_name}_{batch_id}.parquet"

    @overrides
    def _write_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table | pa.RecordBatch,
    ) -> Path:
        """
        Process a record batch.

        Return the path to the cache file.
        """
        output_file_path = self.get_new_cache_file_path(stream_name)
        with pa.parquet.ParquetWriter(output_file_path, record_batch.schema) as writer:
            writer.write_table(cast(pa.Table, record_batch))

        return output_file_path
