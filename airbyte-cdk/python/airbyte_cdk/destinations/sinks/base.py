"""Destination Sink Base Classes."""

from __future__ import annotations

import abc
from collections.abc import Iterable
from typing import Any

from pendulum import now
from typing_extensions import final

from airbyte_cdk import AirbyteMessage
from airbyte_cdk.models import (
    DestinationStats,
)
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sql.shared import CatalogProvider

Record = Any


def _append_destination_record_count(
    state_message: AirbyteMessage,
    record_count: int,
) -> None:
    """Append the number of records written to the state message.

    This is a helper function that can be used to implement the
    `StreamSinkBase.enqueue_state_message` method.
    """
    if state_message.type is not AirbyteMessage.Type.STATE or not state_message.state:
        raise ValueError("state_message must be a state message")

    state_message.state.destinationStats = DestinationStats(record_count)


class StreamSinkBase(abc.ABC):
    """Base class for stream sinks."""

    MAX_BUFFERED_RECORDS = 10_000
    """Maximum number of records to buffer before flushing."""

    MAX_BUFFER_AGE_IN_SECONDS = 60 * 3  # 3 minutes
    """Maximum age of buffered records before flushing."""

    def __init__(
        self,
        stream_name: str,
        *,
        destination_config: dict,
        stream_namespace: str = "",
        catalog_provider: CatalogProvider,
        message_repository: MessageRepository,
    ) -> None:
        self.catalog_provider = catalog_provider
        self.destination_config = destination_config
        self.stream_name = stream_name
        self.stream_namespace = stream_namespace
        self.message_repository = message_repository

        self.records_buffered = 0
        self.records_finalized = 0
        self.last_flush_time = now()

    @property
    def needs_flush(self) -> bool:
        """Return True if there are records buffered and ready to be flushed.

        By default, this method returns True if the number of buffered records exceeds
        `MAX_BUFFERED_RECORDS` or if the time since the last flush exceeds
        `MAX_BUFFER_AGE_IN_SECONDS`.

        Implementations can customize this to flush records based on their own criteria.
        """
        return (
            self.records_buffered >= self.MAX_BUFFERED_RECORDS  # buffer is full
            or self.seconds_since_last_flush >= self.MAX_BUFFER_AGE_IN_SECONDS  # max latency elapsed
        )

    @property
    def seconds_since_last_flush(self) -> int:
        """Return the number of seconds since the last flush."""
        return now().diff(self.last_flush_time).in_seconds()

    def _write_record(self, record: Record) -> None:
        """Write a single record to the sink.

        This method must be implemented by subclasses, unless they override
        `process_records` to write records directly in batches.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def process_records(self, records: Iterable[Record]) -> None:
        """Write a batch of records to the sink.

        This method can be overridden by subclasses to write records in batches.

        The default implementation simply calls `_write_record` for each record.
        """
        for record in records:
            self._write_record(record)

    @final
    def enqueue_state_message(self, state_message: AirbyteMessage) -> None:
        """Add a state message to be emitted after records before it have been flushed.

        The default implementation simply immediately flushes the sink and then emits
        the state message.
        """
        _append_destination_record_count(
            state_message=state_message,
            record_count=self.records_buffered,
        )
        self.flush()
        self.message_repository.emit_message(state_message)

    def finalize_batches(self) -> None:
        """Write any buffered records.

        By default, this is a no-op. Subclasses can override this method to write any
        buffered records before the sink is closed.

        If records are written directly as they are received, then this method should be
        a no-op.
        """
        pass

    @final
    def flush(self) -> None:
        """Flush any buffered records to the sink.

        This method is called when the sink is closed, when a new state message arrives,
        or when the sink is flushed explicitly by the caller (for instance due to resource
        limitations).
        """
        self.finalize_batches()
        self.records_finalized += self.records_buffered
        self.records_buffered = 0
        self.last_flush_time = now()

    def enrich_records(self, records: Iterable[Record]) -> Iterable[Record]:
        """Enrich records before writing to the sink.

        This method can be overridden by subclasses to enrich records before writing them
        to the sink.

        The default implementation simply calls enrich_record() on each record
        sequentially.
        """
        return (self.enrich_record(record) for record in records)

    def enrich_record(self, record: Record) -> Record:
        """Enrich a record before writing it to the sink.

        This method can be overridden by subclasses to enrich records before writing them
        to the sink.

        The default implementation simply returns the record unchanged.

        Subclasses can override this method to add additional fields to the record, for
        instance to add metadata or to transform the record before writing it.

        Alternatively, subclasses can override `enrich_records` to enrich records in
        batches.
        """
        return record
