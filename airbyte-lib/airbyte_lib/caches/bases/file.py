"""Define abstract base class for Caches, which write and read from durable storage."""

from __future__ import annotations

import abc
from pathlib import Path

import pyarrow as pa
from overrides import overrides

from airbyte_lib.bases.core import CacheBase

DEFAULT_BATCH_SIZE = 10000


class FileCacheBase(CacheBase, abc.ABCMeta):
    """A generic base implementation for a file-based cache."""

    @abc.abstractmethod
    def create_file_path(
        self,
        stream_name: str,
        batch_id: str | None = None,  # ULID of the batch
    ) -> Path:
        """Create and return a new cache file path for the given stream."""
        ...

    @abc.abstractmethod
    def write_batch_to_file(
        self,
        stream_name: str,
        record_batch: pa.Table | pa.RecordBatch,
    ) -> Path:
        """Write the provided batch to a cache file.

        Return the path to the written cache file.
        """
        ...

    @abc.abstractmethod
    def process_batch(
        self,
        stream_name: str,
        record_batch: pa.Table,
    ) -> None:
        """Process a single batch."""
        self.write_batch_to_file(stream_name, record_batch)

    @overrides
    def finalize_batches(
        self, stream_name: str, batches: dict[str, BatchHandle]
    ) -> bool:
        """Finalize all uncommitted batches.

        If a stream name is provided, only process uncommitted batches for that stream.
        """
        pass  # Nothing to finalize
