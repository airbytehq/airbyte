# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Define abstract base class for File Writers, which write and read from file storage."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, cast, final

from overrides import overrides

from airbyte_lib._processors import BatchHandle, RecordProcessor
from airbyte_lib.config import CacheConfigBase


if TYPE_CHECKING:
    import pyarrow as pa

    from airbyte_protocol.models import (
        AirbyteStateMessage,
    )


DEFAULT_BATCH_SIZE = 10000


# The batch handle for file writers is a list of Path objects.
@dataclass
class FileWriterBatchHandle(BatchHandle):
    """The file writer batch handle is a list of Path objects."""

    files: list[Path] = field(default_factory=list)


class FileWriterConfigBase(CacheConfigBase):
    """Configuration for the Snowflake cache."""

    cache_dir: Path = Path("./.cache/files/")
    """The directory to store cache files in."""
    cleanup: bool = True
    """Whether to clean up temporary files after processing a batch."""


class FileWriterBase(RecordProcessor, abc.ABC):
    """A generic base implementation for a file-based cache."""

    config_class = FileWriterConfigBase
    config: FileWriterConfigBase

    @abc.abstractmethod
    @overrides
    def _write_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table,
    ) -> FileWriterBatchHandle:
        """Process a record batch.

        Return a list of paths to one or more cache files.
        """
        ...

    @final
    def write_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table,
    ) -> FileWriterBatchHandle:
        """Write a batch of records to the cache.

        This method is final because it should not be overridden.

        Subclasses should override `_write_batch` instead.
        """
        return self._write_batch(stream_name, batch_id, record_batch)

    @overrides
    def _cleanup_batch(
        self,
        stream_name: str,
        batch_id: str,
        batch_handle: BatchHandle,
    ) -> None:
        """Clean up the cache.

        For file writers, this means deleting the files created and declared in the batch.

        This method is a no-op if the `cleanup` config option is set to False.
        """
        if self.config.cleanup:
            batch_handle = cast(FileWriterBatchHandle, batch_handle)
            _ = stream_name, batch_id
            for file_path in batch_handle.files:
                file_path.unlink()

    @final
    def cleanup_batch(
        self,
        stream_name: str,
        batch_id: str,
        batch_handle: BatchHandle,
    ) -> None:
        """Clean up the cache.

        For file writers, this means deleting the files created and declared in the batch.

        This method is final because it should not be overridden.

        Subclasses should override `_cleanup_batch` instead.
        """
        self._cleanup_batch(stream_name, batch_id, batch_handle)

    @overrides
    def _finalize_state_messages(
        self,
        stream_name: str,
        state_messages: list[AirbyteStateMessage],
    ) -> None:
        """
        State messages are not used in file writers, so this method is a no-op.
        """
        pass
