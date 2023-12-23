"""Define abstract base class for Caches, which write and read from durable storage."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, final

from overrides import overrides

from airbyte_lib.config import CacheConfigBase
from airbyte_lib.processors import BatchHandle, RecordProcessor


if TYPE_CHECKING:
    from pathlib import Path

    import pyarrow as pa


DEFAULT_BATCH_SIZE = 10000


# The batch handle for file writers is a list of Path objects.
@dataclass
class FileWriterBatchHandle(BatchHandle):
    """The file writer batch handle is a list of Path objects."""

    files: list[Path] = field(default_factory=list)


class FileWriterConfigBase(CacheConfigBase):
    """Configuration for the Snowflake cache."""

    type: str = "files"
    cache_path: str = "./.cache/files/"


class FileWriterBase(RecordProcessor, abc.ABC):
    """A generic base implementation for a file-based cache."""

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

    @final
    def write_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table | pa.RecordBatch,
    ) -> FileWriterBatchHandle:
        """Write a batch of records to the cache.

        This method is final because it should not be overridden.

        Subclasses should override `_write_batch` instead.
        """
        return self._write_batch(stream_name, batch_id, record_batch)
