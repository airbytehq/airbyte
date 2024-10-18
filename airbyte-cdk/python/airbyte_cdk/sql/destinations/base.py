# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Destination base classes.

For usage examples, see the `airbyte_cdk.sql.destinations` module documentation.
"""

from __future__ import annotations

import warnings
from typing import IO, TYPE_CHECKING, Any, Literal, cast

from airbyte_cdk.models import Type
from airbyte_cdk.sql import exceptions as exc
from airbyte_cdk.sql._connector_base import ConnectorBase
from airbyte_cdk.sql._message_iterators import AirbyteMessageIterator
from airbyte_cdk.sql._util.temp_files import as_temp_files
from airbyte_cdk.sql._writers.base import AirbyteWriterInterface
from airbyte_cdk.sql.caches.util import get_default_cache
from airbyte_cdk.sql.progress import ProgressTracker
from airbyte_cdk.sql.results import ReadResult, WriteResult
from airbyte_cdk.sql.shared.catalog_providers import CatalogProvider
from airbyte_cdk.sql.sources.base import Source
from airbyte_cdk.sql.state_providers import JoinedStateProvider, StateProviderBase, StaticInputState
from airbyte_cdk.sql.state_writers import NoOpStateWriter, StdOutStateWriter
from airbyte_cdk.sql.strategies import WriteStrategy

if TYPE_CHECKING:
    from airbyte_cdk.sql._executors.base import Executor
    from airbyte_cdk.sql.caches.base import CacheBase
    from airbyte_cdk.sql.state_writers import StateWriterBase


class Destination(ConnectorBase, AirbyteWriterInterface):
    """A class representing a destination that can be called."""

    connector_type: Literal["destination"] = "destination"

    def __init__(
        self,
        executor: Executor,
        name: str,
        config: dict[str, Any] | None = None,
        *,
        validate: bool = False,
    ) -> None:
        """Initialize the source.

        If config is provided, it will be validated against the spec if validate is True.
        """
        super().__init__(
            executor=executor,
            name=name,
            config=config,
            validate=validate,
        )

    def write(  # noqa: PLR0912, PLR0915 # Too many arguments/statements
        self,
        source_data: Source | ReadResult,
        *,
        streams: list[str] | Literal["*"] | None = None,
        cache: CacheBase | None | Literal[False] = None,
        state_cache: CacheBase | None | Literal[False] = None,
        write_strategy: WriteStrategy = WriteStrategy.AUTO,
        force_full_refresh: bool = False,
    ) -> WriteResult:
        """Write data from source connector or already cached source data.

        Caching is enabled by default, unless explicitly disabled.

        Args:
            source_data: The source data to write. Can be a `Source` or a `ReadResult` object.
            streams: The streams to write to the destination. If omitted or if "*" is provided,
                all streams will be written. If `source_data` is a source, then streams must be
                selected here or on the source. If both are specified, this setting will override
                the stream selection on the source.
            cache: The cache to use for reading source_data. If `None`, no cache will be used. If
                False, the cache will be disabled. This must be `None` if `source_data` is already
                a `Cache` object.
            state_cache: A cache to use for storing incremental state. You do not need to set this
                if `cache` is specified or if `source_data` is a `Cache` object. Set to `False` to
                disable state management.
            write_strategy: The strategy to use for writing source_data. If `AUTO`, the connector
                will decide the best strategy to use.
            force_full_refresh: Whether to force a full refresh of the source_data. If `True`, any
                existing state will be ignored and all source data will be reloaded.

        For incremental syncs, `cache` or `state_cache` will be checked for matching state values.
        If the cache has tracked state, this will be used for the sync. Otherwise, if there is
        a known destination state, the destination-specific state will be used. If neither are
        available, a full refresh will be performed.
        """
        if not isinstance(source_data, ReadResult | Source):
            raise exc.AirbyteInputError(
                message="Invalid source_data type for `source_data` arg.",
                context={
                    "source_data_type_provided": type(source_data).__name__,
                },
            )

        # Resolve `source`, `read_result`, and `source_name`
        source: Source | None = source_data if isinstance(source_data, Source) else None
        read_result: ReadResult | None = source_data if isinstance(source_data, ReadResult) else None
        source_name: str = source.name if source else cast(ReadResult, read_result).source_name

        # State providers and writers default to no-op, unless overridden below.
        cache_state_provider: StateProviderBase = StaticInputState([])
        """Provides the state of the cache's data."""
        cache_state_writer: StateWriterBase = NoOpStateWriter()
        """Writes updates for the state of the cache's data."""
        destination_state_provider: StateProviderBase = StaticInputState([])
        """Provides the state of the destination's data, from `cache` or `state_cache`."""
        destination_state_writer: StateWriterBase = NoOpStateWriter()
        """Writes updates for the state of the destination's data, to `cache` or `state_cache`."""

        # If caching not explicitly disabled
        if cache is not False:
            # Resolve `cache`, `cache_state_provider`, and `cache_state_writer`
            if isinstance(source_data, ReadResult):
                cache = source_data.cache

            cache = cache or get_default_cache()
            cache_state_provider = cache.get_state_provider(
                source_name=source_name,
                destination_name=None,  # This will just track the cache state
            )
            cache_state_writer = cache.get_state_writer(
                source_name=source_name,
                destination_name=None,  # This will just track the cache state
            )

        # Resolve `state_cache`
        if state_cache is None:
            state_cache = cache or get_default_cache()

        # Resolve `destination_state_writer` and `destination_state_provider`
        if state_cache:
            destination_state_writer = state_cache.get_state_writer(
                source_name=source_name,
                destination_name=self.name,
            )
            if not force_full_refresh:
                destination_state_provider = state_cache.get_state_provider(
                    source_name=source_name,
                    destination_name=self.name,
                )
        elif state_cache is not False:
            warnings.warn(
                "No state backend or cache provided. State will not be tracked."
                "To track state, provide a cache or state backend."
                "To silence this warning, set `state_cache=False` explicitly.",
                category=exc.AirbyteWarning,
                stacklevel=2,
            )

        # Resolve `catalog_provider`
        if source:
            catalog_provider = CatalogProvider(
                configured_catalog=source.get_configured_catalog(
                    streams=streams,
                )
            )
        elif read_result:
            catalog_provider = CatalogProvider.from_read_result(read_result)
        else:
            raise exc.AirbyteInternalError(
                message="`source_data` must be a `Source` or `ReadResult` object.",
            )

        progress_tracker = ProgressTracker(
            source=source if isinstance(source_data, Source) else None,
            cache=cache or None,
            destination=self,
            expected_streams=catalog_provider.stream_names,
        )

        source_state_provider: StateProviderBase
        source_state_provider = JoinedStateProvider(
            primary=cache_state_provider,
            secondary=destination_state_provider,
        )

        if source:
            if cache is False:
                # Get message iterator for source (caching disabled)
                message_iterator: AirbyteMessageIterator = source._get_airbyte_message_iterator(  # noqa: SLF001 # Non-public API
                    streams=streams,
                    state_provider=source_state_provider,
                    progress_tracker=progress_tracker,
                    force_full_refresh=force_full_refresh,
                )
            else:
                # Caching enabled and we are reading from a source.
                # Read the data to cache if caching is enabled.
                read_result = source._read_to_cache(  # noqa: SLF001  # Non-public API
                    cache=cache,
                    state_provider=source_state_provider,
                    state_writer=cache_state_writer,
                    catalog_provider=catalog_provider,
                    stream_names=catalog_provider.stream_names,
                    write_strategy=write_strategy,
                    force_full_refresh=force_full_refresh,
                    skip_validation=False,
                    progress_tracker=progress_tracker,
                )
                message_iterator = AirbyteMessageIterator.from_read_result(
                    read_result=read_result,
                )
        else:  # Else we are reading from a read result
            assert read_result is not None
            message_iterator = AirbyteMessageIterator.from_read_result(
                read_result=read_result,
            )

        # Write the data to the destination
        try:
            self._write_airbyte_message_stream(
                stdin=message_iterator,
                catalog_provider=catalog_provider,
                write_strategy=write_strategy,
                state_writer=destination_state_writer,
                progress_tracker=progress_tracker,
            )
        except Exception as ex:
            progress_tracker.log_failure(exception=ex)
            raise
        else:
            # No exceptions were raised, so log success
            progress_tracker.log_success()

        return WriteResult(
            destination=self,
            source_data=source_data,
            catalog_provider=catalog_provider,
            state_writer=destination_state_writer,
            progress_tracker=progress_tracker,
        )

    def _write_airbyte_message_stream(
        self,
        stdin: IO[str] | AirbyteMessageIterator,
        *,
        catalog_provider: CatalogProvider,
        write_strategy: WriteStrategy,
        state_writer: StateWriterBase | None = None,
        progress_tracker: ProgressTracker,
    ) -> None:
        """Read from the connector and write to the cache."""
        # Run optional validation step
        if state_writer is None:
            state_writer = StdOutStateWriter()

        # Apply the write strategy to the catalog provider before sending to the destination
        catalog_provider = catalog_provider.with_write_strategy(write_strategy)

        with as_temp_files(
            files_contents=[
                self._config,
                catalog_provider.configured_catalog.model_dump_json(),
            ]
        ) as [
            config_file,
            catalog_file,
        ]:
            try:
                # We call the connector to write the data, tallying the inputs and outputs
                for destination_message in progress_tracker.tally_confirmed_writes(
                    messages=self._execute(
                        args=[
                            "write",
                            "--config",
                            config_file,
                            "--catalog",
                            catalog_file,
                        ],
                        stdin=AirbyteMessageIterator(
                            progress_tracker.tally_pending_writes(
                                stdin,
                            )
                        ),
                    )
                ):
                    if destination_message.type is Type.STATE:
                        state_writer.write_state(state_message=destination_message.state)

            except exc.AirbyteConnectorFailedError as ex:
                raise exc.AirbyteConnectorWriteError(
                    connector_name=self.name,
                    log_text=self._last_log_messages,
                    original_exception=ex,
                ) from None


__all__ = [
    "Destination",
]
