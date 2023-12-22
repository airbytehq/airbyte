"""Define abstract base class for Caches, which write and read from durable storage."""

from __future__ import annotations

import abc
from pathlib import Path

import pyarrow as pa
from overrides import overrides  # noqa: F401  # Ignore unused import warning
from airbyte_lib.config import CacheConfigBase  # noqa: F401  # Ignore unused import warning
from airbyte_lib.processors import RecordProcessor, BatchHandle  # noqa: F401  # Ignore unused import warning

DEFAULT_BATCH_SIZE = 10000


# The batch handle for file writers is a list of Path objects.
FileWriterBatchHandle = list[Path]


class FileWriterConfigBase(CacheConfigBase):
    """Configuration for the Snowflake cache."""

    type: str = "files"
    cache_path: str = "./.cache/files/"


class FileWriterBase(RecordProcessor, abc.ABC):
    """A generic base implementation for a file-based cache."""

    # TODO: delete if not needed
    # @abc.abstractmethod
    # def create_file_path(
    #     self,
    #     stream_name: str,
    #     batch_id: str | None = None,  # ULID of the batch
    # ) -> Path:
    #     """Create and return a new cache file path for the given stream."""
    #     ...

    @abc.abstractmethod
    @overrides
    def _write_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table | pa.RecordBatch,
    ) -> FileWriterBatchHandle:
        """
        Process a record batch.

        Return a list of paths to one or more cache files.
        """
        ...
