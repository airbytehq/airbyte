# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A Parquet cache implementation."""
from __future__ import annotations

from pathlib import Path
from typing import cast

import pyarrow as pa
import ulid
from overrides import overrides
from pyarrow import parquet

from .base import FileWriterBase, FileWriterBatchHandle, FileWriterConfigBase


class ParquetWriterConfig(FileWriterConfigBase):
    """Configuration for the Snowflake cache."""

    # Inherits `cache_dir` from base class


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
        target_dir = Path(config.cache_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir / f"{stream_name}_{batch_id}.parquet"

    @overrides
    def _write_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table | pa.RecordBatch,
    ) -> FileWriterBatchHandle:
        """Process a record batch.

        Return the path to the cache file.
        """
        _ = batch_id  # unused
        output_file_path = self.get_new_cache_file_path(stream_name)

        with parquet.ParquetWriter(output_file_path, record_batch.schema) as writer:
            writer.write_table(cast(pa.Table, record_batch))

        batch_handle = FileWriterBatchHandle()
        batch_handle.files.append(output_file_path)
        return batch_handle
