"""Destination Sink Base Classes."""

from __future__ import annotations

import abc
from collections.abc import Iterable
from typing import Any

from pendulum import now
from typing_extensions import final

from airbyte_cdk import AirbyteMessage
from airbyte_cdk.models import (
    ConfiguredAirbyteCatalog,
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
    MAX_BUFFERED_RECORDS = 10_000

    def __init__(
        self,
        stream_name: str,
        *,
        destination_config: dict,
        stream_namespace: str = "",
        catalog_provider: CatalogProvider | ConfiguredAirbyteCatalog,
        message_repository: MessageRepository,
    ) -> None:
        if isinstance(catalog_provider, CatalogProvider):
            self.catalog_provider = catalog_provider
        elif isinstance(catalog_provider, ConfiguredAirbyteCatalog):
            self.catalog_provider = CatalogProvider(catalog=catalog_provider)
        else:
            raise ValueError("catalog_provider must be either CatalogProvider or ConfiguredAirbyteCatalog")

        self.destination_config = destination_config
        self.records_buffered = 0
        self.records_finalized = 0
        self.stream_name = stream_name
        self.stream_namespace = stream_namespace
        self.last_flush_time = 0
        self.message_repository = message_repository

    @property
    def needs_flush(self) -> bool:
        """Return True if there are records buffered and ready to be flushed.

        Implementations can customize this to flush records based on their own criteria.
        """
        return self.records_buffered >= self.MAX_BUFFERED_RECORDS

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


class StreamSinkFactoryBase(abc.ABC):
    """Base class for stream sink factories."""

    default_stream_sink_class: type[StreamSinkBase] = StreamSinkBase

    def create_sink(
        self,
        destination_config: dict,
        stream_name: str,
        stream_namespace: str,
        catalog_provider: CatalogProvider | ConfiguredAirbyteCatalog,
        message_repository: MessageRepository,
    ) -> StreamSinkBase:
        """Create a new stream sink instance.

        By default, this method creates a new instance of the default stream sink class.

        Subclasses can override this method to use a different stream sink class, for
        instance if different stream names or catalog configurations require different
        sink implementations.
        """
        return self.default_stream_sink_class(
            stream_name=stream_name,
            destination_config=destination_config,
            stream_namespace=stream_namespace,
            catalog_provider=catalog_provider,
            message_repository=message_repository,
        )
