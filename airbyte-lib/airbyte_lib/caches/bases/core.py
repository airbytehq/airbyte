"""Define abstract base class for Caches, which write and read from durable storage."""

from __future__ import annotations

import abc
import io
import sys
from typing import final, Any

import orjson
import pyarrow as pa

DEFAULT_BATCH_SIZE = 10000

from overrides import EnforceOverrides

from .config import CacheConfigBase

BatchHandle = Any


class AirbyteMessageParsingError(Exception):
    """Raised when an Airbyte message is invalid or cannot be parsed."""


class CacheBase(abc.AbstractBaseClass, EnforceOverrides):
    """Abstract base class for Caches, which write and read from durable storage."""

    config_class: type[CacheConfigBase]
    skip_finalize_step: bool = False

    def __init__(
        self,
        config: CacheConfigBase | dict,
        **kwargs,  # Added for future proofing purposes.
    ):
        if isinstance(config, dict):
            config = self.config_class(**config)

        if not isinstance(config, self.config_class):
            err_msg = f"Expected config class of type '{self.config_class.__name__}'.  Instead found '{type(config).__name__}'."
            raise RuntimeError(err_msg)

        self.config = self.config_class
        self._uncommitted_batches: dict[dict[str, Any]] = {}
        self._completed_batches: dict[dict[str, Any]] = {}

    @final
    def process_stdin(
        self,
        max_batch_size: int = DEFAULT_BATCH_SIZE,
    ):
        """
        Process the input stream from stdin.

        Return a list of summaries for testing.
        """
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
        return self.process_input_stream(input_stream, max_batch_size)

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
        stream_batches = {}
        processing_summaries = []

        for line in input_stream:
            record = orjson.loads(line)
            try:
                stream_name = record["stream_name"]
            except KeyError:
                raise AirbyteMessageParsingError(f"Record missing stream_name: {record}")

            if stream_name not in stream_batches:
                stream_batches[stream_name] = []

            stream_batch = stream_batches[stream_name]
            stream_batch.append(record)

            if len(stream_batch) >= max_batch_size:
                record_batch = pa.Table.from_pydict(stream_batch)
                summary = self._process_batch(stream_name, record_batch)
                processing_summaries.append(summary)
                stream_batch.clear()

        for stream_name, batch in stream_batches.items():
            if batch:
                record_batch = pa.Table.from_pydict(batch)
                summary = self._process_batch(stream_name, record_batch)
                processing_summaries.append(summary)

        return processing_summaries

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
        batch_handle = self.process_batch(stream_name, batch_id, record_batch) or self.get_batch_handle(stream_name, batch_id)
        if stream_name not in self.processed_batches:
            self.processed_batches[stream_name] = {}

        if not self.skip_commit_step:
            self._completed_batches[stream_name][batch_id] = batch_handle
        else:
            self._uncommitted_batches[stream_name][batch_id] = batch_handle

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
        return ulid.new().str

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

    @final
    def _finalize_batches(self, stream_name: str) -> dict[str, BatchHandle]:
        """Commit all uncommitted batches for a given stream."""
        batches_to_finalize = self._uncommitted_batches[stream_name]
        self.finalize_batches(stream_name, batches_to_finalize)
        self._committed_batches.update(batches_to_finalize)
        self._uncommitted_batches.clear()
        return batches_to_finalize

    @abc.abstractmethod
    def finalize_batches(self, stream_name: str, batches: dict[str, BatchHandle]) -> bool:
        """Finalize all uncommitted batches.

        If a stream name is provided, only process uncommitted batches for that stream.
        """
