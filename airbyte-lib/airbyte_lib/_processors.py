# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Define abstract base class for Processors, including Caches and File writers.

Processors can all take input from STDIN or a stream of Airbyte messages.

Caches will pass their input to the File Writer. They share a common base class so certain
abstractions like "write" and "finalize" can be handled in either layer, or both.
"""

from __future__ import annotations

import abc
import contextlib
import io
import sys
from collections import defaultdict
from typing import TYPE_CHECKING, Any, cast, final

import pyarrow as pa
import ulid

from airbyte_protocol.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    Type,
)

from airbyte_lib._util import protocol_util  # Internal utility functions


if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Iterator

    from airbyte_lib.config import CacheConfigBase


DEFAULT_BATCH_SIZE = 10000


class BatchHandle:
    pass


class AirbyteMessageParsingError(Exception):
    """Raised when an Airbyte message is invalid or cannot be parsed."""


class RecordProcessor(abc.ABC):
    """Abstract base class for classes which can process input records."""

    config_class: type[CacheConfigBase]
    skip_finalize_step: bool = False

    def __init__(
        self,
        config: CacheConfigBase | dict | None,
    ) -> None:
        if isinstance(config, dict):
            config = self.config_class(**config)

        self.config = config or self.config_class()
        if not isinstance(self.config, self.config_class):
            err_msg = (
                f"Expected config class of type '{self.config_class.__name__}'.  "
                f"Instead found '{type(self.config).__name__}'."
            )
            raise TypeError(err_msg)

        self.source_catalog: ConfiguredAirbyteCatalog | None = None

        self._pending_batches: dict[str, dict[str, Any]] = defaultdict(lambda: {}, {})
        self._finalized_batches: dict[str, dict[str, Any]] = defaultdict(lambda: {}, {})

        self._pending_state_messages: dict[str, list[AirbyteStateMessage]] = defaultdict(list, {})
        self._finalized_state_messages: dict[
            str,
            list[AirbyteStateMessage],
        ] = defaultdict(list, {})

        self._setup()

    def register_source(
        self,
        source_name: str,
        source_catalog: ConfiguredAirbyteCatalog,
    ) -> None:
        """Register the source name and catalog.

        For now, only one source at a time is supported.
        If this method is called multiple times, the last call will overwrite the previous one.

        TODO: Expand this to handle mutliple sources.
        """
        _ = source_name
        self.source_catalog = source_catalog

    @final
    def process_stdin(
        self,
        max_batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """Process the input stream from stdin.

        Return a list of summaries for testing.
        """
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
        self.process_input_stream(input_stream, max_batch_size)

    @final
    def _airbyte_messages_from_buffer(
        self,
        buffer: io.TextIOBase,
    ) -> Iterator[AirbyteMessage]:
        """Yield messages from a buffer."""
        yield from (AirbyteMessage.parse_raw(line) for line in buffer)

    @final
    def process_input_stream(
        self,
        input_stream: io.TextIOBase,
        max_batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """Parse the input stream and process data in batches.

        Return a list of summaries for testing.
        """
        messages = self._airbyte_messages_from_buffer(input_stream)
        self.process_airbyte_messages(messages, max_batch_size)

    @final
    def process_airbyte_messages(
        self,
        messages: Iterable[AirbyteMessage],
        max_batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        stream_batches: dict[str, list[dict]] = defaultdict(list, {})

        # Process messages, writing to batches as we go
        for message in messages:
            if message.type is Type.RECORD:
                record_msg = cast(AirbyteRecordMessage, message.record)
                stream_name = record_msg.stream
                stream_batch = stream_batches[stream_name]
                stream_batch.append(protocol_util.airbyte_record_message_to_dict(record_msg))

                if len(stream_batch) >= max_batch_size:
                    record_batch = pa.Table.from_pylist(stream_batch)
                    self._process_batch(stream_name, record_batch)
                    stream_batch.clear()

            elif message.type is Type.STATE:
                state_msg = cast(AirbyteStateMessage, message.state)
                if state_msg.type in [AirbyteStateType.GLOBAL, AirbyteStateType.LEGACY]:
                    self._pending_state_messages[f"_{state_msg.type}"].append(state_msg)
                else:
                    stream_state = cast(AirbyteStreamState, state_msg.stream)
                    stream_name = stream_state.stream_descriptor.name
                    self._pending_state_messages[stream_name].append(state_msg)

            elif message.type in [Type.LOG, Type.TRACE]:
                pass

            else:
                raise ValueError(f"Unexpected message type: {message.type}")

        # We are at the end of the stream. Process whatever else is queued.
        for stream_name, batch in stream_batches.items():
            if batch:
                record_batch = pa.Table.from_pylist(batch)
                self._process_batch(stream_name, record_batch)

        # Finalize any pending batches
        for stream_name in list(self._pending_batches.keys()):
            self._finalize_batches(stream_name)

    @final
    def _process_batch(
        self,
        stream_name: str,
        record_batch: pa.Table,
    ) -> tuple[str, Any, Exception | None]:
        """Process a single batch.

        Returns a tuple of the batch ID, batch handle, and an exception if one occurred.
        """
        batch_id = self._new_batch_id()
        batch_handle = self._write_batch(
            stream_name,
            batch_id,
            record_batch,
        ) or self._get_batch_handle(stream_name, batch_id)

        if self.skip_finalize_step:
            self._finalized_batches[stream_name][batch_id] = batch_handle
        else:
            self._pending_batches[stream_name][batch_id] = batch_handle

        return batch_id, batch_handle, None

    @abc.abstractmethod
    def _write_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table | pa.RecordBatch,
    ) -> BatchHandle:
        """Process a single batch.

        Returns a batch handle, such as a path or any other custom reference.
        """

    def _cleanup_batch(  # noqa: B027  # Intentionally empty, not abstract
        self,
        stream_name: str,
        batch_id: str,
        batch_handle: BatchHandle,
    ) -> None:
        """Clean up the cache.

        This method is called after the given batch has been finalized.

        For instance, file writers can override this method to delete the files created. Caches,
        similarly, can override this method to delete any other temporary artifacts.
        """
        pass

    def _new_batch_id(self) -> str:
        """Return a new batch handle."""
        return str(ulid.ULID())

    def _get_batch_handle(
        self,
        stream_name: str,
        batch_id: str | None = None,  # ULID of the batch
    ) -> str:
        """Return a new batch handle.

        By default this is a concatenation of the stream name and batch ID.
        However, any Python object can be returned, such as a Path object.
        """
        batch_id = batch_id or self._new_batch_id()
        return f"{stream_name}_{batch_id}"

    def _finalize_batches(self, stream_name: str) -> dict[str, BatchHandle]:
        """Finalize all uncommitted batches.

        Returns a mapping of batch IDs to batch handles, for processed batches.

        This is a generic implementation, which can be overridden.
        """
        with self._finalizing_batches(stream_name) as batches_to_finalize:
            if batches_to_finalize and not self.skip_finalize_step:
                raise NotImplementedError(
                    "Caches need to be finalized but no _finalize_batch() method "
                    f"exists for class {self.__class__.__name__}",
                )

            return batches_to_finalize

    @final
    @contextlib.contextmanager
    def _finalizing_batches(
        self,
        stream_name: str,
    ) -> Generator[dict[str, BatchHandle], str, None]:
        """Context manager to use for finalizing batches, if applicable.

        Returns a mapping of batch IDs to batch handles, for those processed batches.
        """
        batches_to_finalize = self._pending_batches[stream_name].copy()
        state_messages_to_finalize = self._pending_state_messages[stream_name].copy()
        self._pending_batches[stream_name].clear()
        self._pending_state_messages[stream_name].clear()
        yield batches_to_finalize

        self._finalized_batches[stream_name].update(batches_to_finalize)
        self._finalized_state_messages[stream_name] += state_messages_to_finalize

        for batch_id, batch_handle in batches_to_finalize.items():
            self._cleanup_batch(stream_name, batch_id, batch_handle)

    def _setup(self) -> None:  # noqa: B027  # Intentionally empty, not abstract
        """Create the database.

        By default this is a no-op but subclasses can override this method to prepare
        any necessary resources.
        """

    def _teardown(self) -> None:
        """Teardown the processor resources.

        By default, the base implementation simply calls _cleanup_batch() for all pending batches.
        """
        for stream_name, pending_batches in self._pending_batches.items():
            for batch_id, batch_handle in pending_batches.items():
                self._cleanup_batch(
                    stream_name=stream_name,
                    batch_id=batch_id,
                    batch_handle=batch_handle,
                )

    @final
    def __del__(self) -> None:
        """Teardown temporary resources when instance is unloaded from memory."""
        self._teardown()
