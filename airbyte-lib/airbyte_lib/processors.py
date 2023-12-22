"""Define abstract base class for Caches, which write and read from durable storage."""

from __future__ import annotations

import abc
import io
import sys
from collections import defaultdict
from typing import final, Any, Iterable, Generator

import pyarrow as pa
import ulid
from overrides import EnforceOverrides

from airbyte_protocol.models import AirbyteRecordMessage, AirbyteMessage, AirbyteStateMessage, Type, ConfiguredAirbyteCatalog

from airbyte_lib.config import CacheConfigBase
import contextlib
from airbyte_lib import _util  # Internal utility functions

DEFAULT_BATCH_SIZE = 10000

BatchHandle = Any



class AirbyteMessageParsingError(Exception):
    """Raised when an Airbyte message is invalid or cannot be parsed."""


class RecordProcessor(abc.ABC, EnforceOverrides):
    """Abstract base class for classes which can process input records."""

    config_class: type[CacheConfigBase]
    skip_finalize_step: bool = False

    def __init__(
        self,
        config: CacheConfigBase | dict | None,
        source_catalog: ConfiguredAirbyteCatalog | None,  # TODO: Better typing for ConfiguredAirbyteCatalog
        **kwargs,  # Added for future proofing purposes.
    ):
        if isinstance(config, dict):
            config = self.config_class(**config)

        if not isinstance(config, self.config_class):
            err_msg = f"Expected config class of type '{self.config_class.__name__}'.  Instead found '{type(config).__name__}'."
            raise RuntimeError(err_msg)

        self.config = config or self.config_class()
        self.source_catalog = source_catalog
        if not self.source_catalog:
            # TODO: Consider a warning here that the cache will not be able to capture
            #       any metadata if catalog is omitted.
            pass

        self._pending_batches: dict[str, dict[str, Any]] = defaultdict(lambda: {}, {})
        self._finalized_batches: dict[str, dict[str, Any]] = defaultdict(lambda: {}, {})

        self._pending_state_messages: dict[str, list[AirbyteStateMessage]] = defaultdict(lambda: [], {})
        self._finalized_state_messages: dict[str, list[AirbyteStateMessage]] = defaultdict(lambda: [], {})

    @final
    def process_stdin(
        self,
        max_batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """
        Process the input stream from stdin.

        Return a list of summaries for testing.
        """
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
        self.process_input_stream(input_stream, max_batch_size)

    @final
    def _airbyte_messages_from_buffer(self, buffer: io.TextIOBase) -> Iterable[AirbyteMessage]:
        """Yield messages from a buffer."""
        yield from {AirbyteMessage.parse_raw(line) for line in buffer}

    @final
    def process_input_stream(
        self,
        input_stream: io.TextIOBase,
        max_batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """
        Parse the input stream and process data in batches.

        Return a list of summaries for testing.
        """
        messages = self._airbyte_messages_from_buffer(input_stream)
        self.process_airbyte_messages(messages, max_batch_size)

    @final
    def process_airbyte_messages(self,
            messages: Iterable[AirbyteMessage],
            max_batch_size: int = DEFAULT_BATCH_SIZE,
        ) -> None:
        stream_batches: dict[str, list[AirbyteRecordMessage]] = defaultdict(lambda: [], {})

        for message in messages:
            if message.type is Type.RECORD:
                record_msg = message.record
                stream_name = record_msg.stream
                stream_batch = stream_batches[stream_name]
                stream_batch.append(_util.airbyte_record_message_to_dict(record_msg))

                if len(stream_batch) >= max_batch_size:
                    record_batch = pa.Table.from_pylist(stream_batch)
                    self._process_batch(stream_name, record_batch)
                    stream_batch.clear()

            elif message.type is Type.STATE:
                state_msg = message.state
                stream_name = state_msg.stream
                self._pending_state_messages[stream_name].append(state_msg)

            else:
                raise ValueError(f"Unexpected message type: {message.type}")

        for stream_name, batch in stream_batches.items():
            if batch:
                record_batch = pa.Table.from_pylist(batch)
                self._process_batch(stream_name, record_batch)

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
            stream_name, batch_id, record_batch
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

        If a stream name is provided, only process uncommitted batches for that stream.

        This is a generic 'final' implementation, which should not be overridden by subclasses.

        Returns a mapping of batch IDs to batch handles, for those batches that were processed.
        """
        with self._finalizing_batches(stream_name) as batches_to_finalize:
            if batches_to_finalize and not self.skip_finalize_step:
                raise NotImplementedError(
                    "Caches need to be finalized but no _finalize_batch() method "
                    f"exists for class {self.__class__.__name__}"
                )

            return batches_to_finalize


    @final
    @contextlib.contextmanager
    def _finalizing_batches(self, stream_name: str) -> Generator[dict[str, BatchHandle], str, None] :
        """Context manager to use for finalizing batches, if applicable.
        
        Returns a mapping of batch IDs to batch handles, for those batches that were processed.
        """
        batches_to_finalize = self._pending_batches[stream_name].copy()
        state_messages_to_finalize = self._pending_state_messages[stream_name].copy()
        self._pending_batches[stream_name].clear()
        self._pending_state_messages[stream_name].clear()
        yield batches_to_finalize

        self._finalized_batches[stream_name].update(batches_to_finalize)
        self._finalized_state_messages[stream_name].append(state_messages_to_finalize)
