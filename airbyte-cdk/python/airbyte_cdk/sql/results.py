# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Module which defines the `ReadResult` and `WriteResult` classes.

These classes are used to return information about read and write operations, respectively. They
contain information such as the number of records read or written, the cache object, and the
state handlers for a sync.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from airbyte_cdk.sql.datasets._sql import CachedDataset


if TYPE_CHECKING:
    from collections.abc import Iterator

    from sqlalchemy.engine import Engine

    from airbyte_cdk.sql._writers.base import AirbyteWriterInterface
    from airbyte_cdk.sql.caches import CacheBase
    from airbyte_cdk.sql.destinations.base import Destination
    from airbyte_cdk.sql.progress import ProgressTracker
    from airbyte_cdk.sql.shared.catalog_providers import CatalogProvider
    from airbyte_cdk.sql.state_providers import StateProviderBase
    from airbyte_cdk.sql.state_writers import StateWriterBase
    from airbyte_cdk.sql.sources.base import Source


class ReadResult(Mapping[str, CachedDataset]):
    """The result of a read operation.

    This class is used to return information about the read operation, such as the number of
    records read. It should not be created directly, but instead returned by the write method
    of a destination.
    """

    def __init__(
        self,
        *,
        source_name: str,
        processed_streams: list[str],
        cache: CacheBase,
        progress_tracker: ProgressTracker,
    ) -> None:
        """Initialize a read result.

        This class should not be created directly. Instead, it should be returned by the `read`
        method of the `Source` class.
        """
        self.source_name = source_name
        self._progress_tracker = progress_tracker
        self._cache = cache
        self._processed_streams = processed_streams

    def __getitem__(self, stream: str) -> CachedDataset:
        """Return the cached dataset for a given stream name."""
        if stream not in self._processed_streams:
            raise KeyError(stream)

        return CachedDataset(self._cache, stream)

    def __contains__(self, stream: object) -> bool:
        """Return whether a given stream name was included in processing."""
        if not isinstance(stream, str):
            return False

        return stream in self._processed_streams

    def __iter__(self) -> Iterator[str]:
        """Return an iterator over the stream names that were processed."""
        return self._processed_streams.__iter__()

    def __len__(self) -> int:
        """Return the number of streams that were processed."""
        return len(self._processed_streams)

    def get_sql_engine(self) -> Engine:
        """Return the SQL engine used by the cache."""
        return self._cache.get_sql_engine()

    @property
    def processed_records(self) -> int:
        """The total number of records read from the source."""
        return self._progress_tracker.total_records_read

    @property
    def streams(self) -> Mapping[str, CachedDataset]:
        """Return a mapping of stream names to cached datasets."""
        return {stream_name: CachedDataset(self._cache, stream_name) for stream_name in self._processed_streams}

    @property
    def cache(self) -> CacheBase:
        """Return the cache object."""
        return self._cache


class WriteResult:
    """The result of a write operation.

    This class is used to return information about the write operation, such as the number of
    records written. It should not be created directly, but instead returned by the write method
    of a destination.
    """

    def __init__(
        self,
        *,
        destination: AirbyteWriterInterface | Destination,
        source_data: Source | ReadResult,
        catalog_provider: CatalogProvider,
        state_writer: StateWriterBase,
        progress_tracker: ProgressTracker,
    ) -> None:
        """Initialize a write result.

        This class should not be created directly. Instead, it should be returned by the `write`
        method of the `Destination` class.
        """
        self._destination: AirbyteWriterInterface | Destination = destination
        self._source_data: Source | ReadResult = source_data
        self._catalog_provider: CatalogProvider = catalog_provider
        self._state_writer: StateWriterBase = state_writer
        self._progress_tracker: ProgressTracker = progress_tracker

    @property
    def processed_records(self) -> int:
        """The total number of records written to the destination."""
        return self._progress_tracker.total_destination_records_delivered

    def get_state_provider(self) -> StateProviderBase:
        """Return the state writer as a state provider.

        As a public interface, we only expose the state writer as a state provider. This is because
        the state writer itself is only intended for internal use. As a state provider, the state
        writer can be used to read the state artifacts that were written. This can be useful for
        testing or debugging.
        """
        return self._state_writer
