"""A DuckDB implementation of the cache."""

from __future__ import annotations

from typing import cast

import pyarrow as pa
from overrides import overrides

from airbyte_lib.caches.duckdb import DuckDBCacheBase, DuckDBCacheConfig
from airbyte_lib.file_writers import (
    FileWriterBase,
    FileWriterBatchHandle,
    FileWriterConfigBase,
)


class InMemoryCacheConfig(DuckDBCacheConfig):
    """Configuration for the in-memory cache."""

    type: str = "in_memory"
    # FIXME: This option doesn't work yet.
    db_path: str = ":memory:"
    # Workaround:
    # db_path: str = "./.output/temp/in_memory.db"



class InMemoryFileWriterConfig(FileWriterConfigBase):
    """Configuration for the in-memory cache."""

    type: str = "in_memory"


class InMemoryFileWriterEmulator(FileWriterBase):
    """The in-memory cache file writer writes to RAM files."""

    config_class = InMemoryFileWriterConfig

    @overrides
    def _write_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table | pa.RecordBatch,
    ) -> InMemoryBatchHandle:
        """
        Process a record batch.

        Return the path to the cache file.
        """
        _ = stream_name, batch_id
        batch_handle = InMemoryBatchHandle()
        batch_handle.pyarrow_table = cast(pa.Table, record_batch)
        return batch_handle


class InMemoryBatchHandle(FileWriterBatchHandle):
    """The in-memory cache batch handle is a list of dicts."""

    pyarrow_table: pa.Table


class InMemoryCache(DuckDBCacheBase):
    """The in-memory cache is accepting airbyte messages and stores them in a dictionary for streams (one list of dicts per stream)."""

    config_class = InMemoryCacheConfig
    file_writer_class = InMemoryFileWriterEmulator

    # FIXME: This option doesn't work yet.
    use_singleton_connection = True  # Dropped connection will lose data

    @overrides
    def _write_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table | pa.RecordBatch,
    ) -> InMemoryBatchHandle:
        """
        Process a record batch.

        Return the path to the cache file.
        """
        _ = stream_name, batch_id
        batch_handle = InMemoryBatchHandle()
        batch_handle.pyarrow_table = cast(pa.Table, record_batch)
        return batch_handle
