"""Define abstract base class for Caches, which write and read from durable storage."""

from __future__ import annotations

import abc
import io
import sys
from collections import defaultdict
from typing import final, Any, cast

import orjson
import pyarrow as pa
import ulid
from overrides import EnforceOverrides

from airbyte_lib.caches.bases.config import CacheConfigBase

DEFAULT_BATCH_SIZE = 10000

BatchHandle = Any


class AirbyteMessageParsingError(Exception):
    """Raised when an Airbyte message is invalid or cannot be parsed."""


class CacheBase(abc.ABC, EnforceOverrides):
    """Abstract base class for Caches, which write and read from durable storage."""

    config_class: type[CacheConfigBase]
    skip_finalize_step: bool = False

    def __init__(
        self,
        config: CacheConfigBase | dict,
        source_catalog: dict[str, Any],  # TODO: Better typing for ConfiguredAirbyteCatalog
        **kwargs,  # Added for future proofing purposes.
    ):
        if isinstance(config, dict):
            config = self.config_class(**config)

        if not isinstance(config, self.config_class):
            err_msg = f"Expected config class of type '{self.config_class.__name__}'.  Instead found '{type(config).__name__}'."
            raise RuntimeError(err_msg)

        self.config = config
        self.source_catalog = source_catalog

        self._pending_batches: dict[str, dict[str, Any]] = defaultdict(lambda: {}, {})
        self._completed_batches: dict[str, dict[str, Any]] = defaultdict(lambda: {}, {})

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
    def process_input_stream(
        self,
        input_stream: io.TextIOBase,
        max_batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """
        Parse the input stream and process data in batches.

        Return a list of summaries for testing.
        """
        stream_batches: dict[str, Any] = {}

        for line in input_stream:
            record = orjson.loads(line)
            try:
                stream_name = record["stream_name"]
            except KeyError:
                raise AirbyteMessageParsingError(
                    f"Record missing stream_name: {record}"
                )

            if stream_name not in stream_batches:
                stream_batches[stream_name] = []

            stream_batch = stream_batches[stream_name]
            stream_batch.append(record)

            if len(stream_batch) >= max_batch_size:
                record_batch = pa.Table.from_pydict(stream_batch)
                self._process_batch(stream_name, record_batch)
                stream_batch.clear()

        for stream_name, batch in stream_batches.items():
            if batch:
                record_batch = pa.Table.from_pydict(batch)
                self._process_batch(stream_name, record_batch)

        for stream_name in self._pending_batches:
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
        batch_id = self.new_batch_id()
        batch_handle = self.process_batch(
            stream_name, batch_id, record_batch
        ) or self.get_batch_handle(stream_name, batch_id)

        if stream_name not in self._pending_batches:
            self._pending_batches[stream_name] = {}

        if not self.skip_finalize_step:
            self._completed_batches[stream_name][batch_id] = batch_handle
        else:
            self._pending_batches[stream_name][batch_id] = batch_handle

        return batch_id, batch_handle, None

    @abc.abstractmethod
    def process_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table,
    ) -> BatchHandle:
        """Process a single batch.

        Returns a batch handle, such as a path or any other custom reference.
        """
        raise NotImplementedError()

    def new_batch_id(self) -> str:
        """Return a new batch handle."""
        return str(ulid.ULID())

    def get_batch_handle(
        self,
        stream_name: str,
        batch_id: str | None = None,  # ULID of the batch
    ) -> str:
        """Return a new batch handle.

        By default this is a concatenation of the stream name and batch ID.
        However, any Python object can be returned, such as a Path object.
        """
        batch_id = batch_id or self.new_batch_id()
        return f"{stream_name}_{batch_id}"

    def _finalize_batches(self, stream_name: str) -> dict[str, BatchHandle]:
        """Commit all uncommitted batches for a given stream.
        
        Returns a mapping of batch IDs to batch handles, for those batches that were processed.
        """
        batches_to_finalize = self._pending_batches[stream_name]
        self._completed_batches.update(batches_to_finalize)
        self._pending_batches.clear()
        return batches_to_finalize
