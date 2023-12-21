"""Define abstract base class for Caches, which write and read from durable storage."""

from __future__ import annotations

import abc
from pathlib import Path

import pyarrow as pa
from overrides import overrides  # noqa: F401  # Ignore unused import warning
from airbyte_lib.config import CacheConfigBase  # noqa: F401  # Ignore unused import warning
from airbyte_lib.processors import RecordProcessor, BatchHandle  # noqa: F401  # Ignore unused import warning

DEFAULT_BATCH_SIZE = 10000


class FileWriterConfigBase(CacheConfigBase):
    """Configuration for the Snowflake cache."""

    type: str = "files"
    cache_path: str


class FileWriterBase(RecordProcessor, abc.ABCMeta):
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
        batch_id: str,
        record_batch: pa.Table,
    ) -> None:
        """Process a single batch."""
        self.write_batch_to_file(stream_name, record_batch)
