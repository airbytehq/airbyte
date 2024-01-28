# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A No-Op (Null) cache implementation.

This is designed to test the raw throughput of a source, without any slowdown from writing files.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from overrides import overrides

from .base import FileWriterBase, FileWriterBatchHandle, FileWriterConfigBase


if TYPE_CHECKING:
    import pyarrow as pa

    from airbyte_lib._processors import BatchHandle


class NullWriterConfig(FileWriterConfigBase):
    """Configuration for the Snowflake cache."""

    # Inherits `cache_dir` from base class


class NullWriter(FileWriterBase):
    """A Parquet cache implementation."""

    config_class = NullWriterConfig

    def get_new_cache_file_path(
        self,
        stream_name: str,
        batch_id: str | None = None,  # ULID of the batch
    ) -> Path:
        """Return a dummy path object."""
        _ = stream_name, batch_id  # unused
        return Path("/not/a/real/file")

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
        _ = batch_id, record_batch  # unused
        output_file_path = self.get_new_cache_file_path(stream_name)

        batch_handle = FileWriterBatchHandle()
        batch_handle.files.append(output_file_path)
        return batch_handle

    @overrides
    def _cleanup_batch(self, stream_name: str, batch_id: str, batch_handle: BatchHandle) -> None:
        _ = stream_name, batch_id, batch_handle  # unused
        pass

    def _table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        _ = table_name
        return True

    def _get_tables_list(self) -> list[str]:
        """Get a list of tables."""
        return []
