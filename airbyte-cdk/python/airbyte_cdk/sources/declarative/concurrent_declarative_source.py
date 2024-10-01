#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import copy
import logging
from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    SyncMode,
)
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor, DeclarativeCursor
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.types import ConnectionDefinition
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.adapters import CursorPartitionGenerator, StreamPartitionGenerator
from airbyte_cdk.sources.streams.concurrent.availability_strategy import AlwaysAvailableAvailabilityStrategy
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor, CursorField, CursorValueType, GapType
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import (
    CustomOutputFormatConcurrentStreamStateConverter,
)
from isodate import parse_duration


@dataclass
class DeclarativeCursorAttributes:
    cursor_field: CursorField
    datetime_format: str
    slice_boundary_fields: Optional[Tuple[str, str]]
    start: Optional[CursorValueType]
    end_provider: Callable[[], CursorValueType]
    lookback_window: Optional[GapType]
    slice_range: Optional[GapType]
    cursor_granularity: Optional[GapType]


class ConcurrentDeclarativeSource(ManifestDeclarativeSource):
    def __init__(
        self,
        catalog: Optional[ConfiguredAirbyteCatalog],
        config: Optional[Mapping[str, Any]],
        state: TState,
        source_config: ConnectionDefinition,
        debug: bool = False,
        emit_connector_builder_messages: bool = False,
        component_factory: Optional[ModelToComponentFactory] = None,
        **kwargs,
    ):
        super().__init__(
            source_config=source_config,
            debug=debug,
            emit_connector_builder_messages=emit_connector_builder_messages,
            component_factory=component_factory,
        )

        self._state = state

        # Alternatively if we don't want to modify run.py, we can separate and instantiate the ConcurrentSource
        self._concurrent_streams, self._synchronous_streams = self._separate_streams(config=config)

        # temporarily hard coding, but once 45943 is merged we need to do the following:
        # concurrency_level_component = factory.create_component(
        #         model_type=ConcurrencyLevelModel, component_definition=self._source_config["concurrency_level"], config=config
        #     )
        # concurrency_level = concurrency_level_component.get_concurrency_level()
        concurrency_level = 10  # self._concurrency_level(config=config)

        self._concurrent_source = ConcurrentSource.create(
            num_workers=concurrency_level,
            initial_number_of_partitions_to_generate=concurrency_level // 2,
            logger=self.logger,
            slice_logger=self._slice_logger,
            message_repository=self.message_repository,
        )

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[Union[List[AirbyteStateMessage], MutableMapping[str, Any]]] = None,
    ) -> Iterator[AirbyteMessage]:

        # ConcurrentReadProcessor pops streams that are finished being read so before syncing, the names of the concurrent
        # streams must be saved so that they can be removed from the catalog before starting synchronous streams
        concurrent_stream_names = set([concurrent_stream.name for concurrent_stream in self._concurrent_streams])

        selected_concurrent_streams = self._select_streams(streams=self._concurrent_streams, configured_catalog=catalog)
        # It would appear that passing in an empty set of streams causes an infinite loop in ConcurrentReadProcessor.
        # This is also evident in concurrent_source_adapter.py so I'll leave this out of scope to fix for now
        if selected_concurrent_streams:
            yield from self._concurrent_source.read(selected_concurrent_streams)

        # Sync all streams that are not concurrent compatible. We filter out concurrent streams because the
        # existing AbstractSource.read() implementation iterates over the catalog when syncing streams. Many
        # of which were already synced using the Concurrent CDK
        filtered_catalog = self._remove_concurrent_streams_from_catalog(catalog=catalog, concurrent_stream_names=concurrent_stream_names)
        yield from super().read(logger, config, filtered_catalog, state)

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        # I don't think should need to be overwritten because I added all_streams() and the underlying check ->
        # CheckStream.check_connection() should invoke all_streams(). It should also sort of be a no-op because
        # we've effectively deprecated availability_strategy as a concept which is all the ConnectionChecker does
        return super().check(logger=logger, config=config)

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        return AirbyteCatalog(streams=[stream.as_airbyte_stream() for stream in self.all_streams(config=config)])

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Returns the list of streams that can be run synchronously in the Python CDK.

        NOTE: For ConcurrentDeclarativeSource, this method only returns synchronous streams because it usage is invoked within the
        existing Python CDK. Streams that support concurrency are started from read().
        """
        return self._synchronous_streams

    def all_streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return self._synchronous_streams + self._concurrent_streams

    def _separate_streams(self, config: Mapping[str, Any]) -> (List[AbstractStream], List[Stream]):
        concurrent_streams: List[AbstractStream] = []
        synchronous_streams: List[Stream] = []

        state_manager = ConnectorStateManager(state=self._state)

        for declarative_stream in super().streams(config=config):
            # Some low-code sources use a combination of DeclarativeStream and regular Python streams. We can't inspect
            # these legacy Python streams the way we do low-code streams to determine if they are concurrent compatible,
            # so we need to treat them as synchronous
            if isinstance(declarative_stream, DeclarativeStream):
                declarative_cursor_attributes = self._get_cursor_attributes(declarative_stream=declarative_stream, config=config)
                if declarative_cursor_attributes:
                    stream_state = state_manager.get_stream_state(
                        stream_name=declarative_stream.name, namespace=declarative_stream.namespace
                    )

                    cursor = ConcurrentCursor(
                        stream_name=declarative_stream.name,
                        stream_namespace=declarative_stream.namespace,
                        stream_state=stream_state,
                        message_repository=self.message_repository,
                        connector_state_manager=state_manager,
                        connector_state_converter=CustomOutputFormatConcurrentStreamStateConverter(
                            datetime_format=declarative_cursor_attributes.datetime_format,
                            is_sequential_state=False,
                            cursor_granularity=declarative_cursor_attributes.cursor_granularity,
                        ),
                        cursor_field=declarative_cursor_attributes.cursor_field,
                        slice_boundary_fields=declarative_cursor_attributes.slice_boundary_fields,
                        start=declarative_cursor_attributes.start,
                        end_provider=declarative_cursor_attributes.end_provider,
                        lookback_window=declarative_cursor_attributes.lookback_window,
                        slice_range=declarative_cursor_attributes.slice_range,
                        cursor_granularity=declarative_cursor_attributes.cursor_granularity,
                    )

                    # todo: This needs to be replaced with a partition generator that invokes cursor.generate_slices()
                    partition_generator = CursorPartitionGenerator(
                        stream=declarative_stream,
                        message_repository=self.message_repository,
                        cursor_field=[declarative_cursor_attributes.cursor_field]
                        if declarative_cursor_attributes.cursor_field is not None
                        else None,
                        cursor=cursor,
                    )

                    concurrent_streams.append(
                        DefaultStream(
                            partition_generator=partition_generator,
                            name=declarative_stream.name,
                            json_schema=declarative_stream.get_json_schema(),
                            availability_strategy=AlwaysAvailableAvailabilityStrategy(),
                            primary_key=declarative_stream.primary_key,
                            cursor_field=declarative_cursor_attributes.cursor_field.cursor_field_key,
                            logger=self.logger,
                            cursor=cursor,
                        )
                    )
                else:
                    synchronous_streams.append(declarative_stream)
            else:
                synchronous_streams.append(declarative_stream)

        return concurrent_streams, synchronous_streams

    def _get_cursor_attributes(
        self, declarative_stream: DeclarativeStream, config: Mapping[str, Any]
    ) -> Optional[DeclarativeCursorAttributes]:
        declarative_cursor = self._get_cursor(stream=declarative_stream)

        if isinstance(declarative_cursor, DatetimeBasedCursor) and type(declarative_cursor) is DatetimeBasedCursor:
            # Only incremental non-substreams are supported. Custom DatetimeBasedCursors are also not supported yet
            # because their behavior can deviate from ConcurrentBehavior

            slice_boundary_fields = (
                declarative_cursor.get_partition_field_start().eval(config=config),
                declarative_cursor.get_partition_field_end().eval(config=config),
            )

            interpolated_state_date = declarative_cursor.get_start_datetime()
            start_date = interpolated_state_date.get_datetime(config=config)

            interpolated_end_date = declarative_cursor.get_end_datetime()
            end_date_provider = partial(interpolated_end_date.get_datetime, config)

            # DatetimeBasedCursor returns an isodate.Duration if step uses month or year precision. This still works in our
            # code, but mypy may complain when we actually implement this in the concurrent low-code source. To fix this, we
            # may need to convert a Duration to timedelta by multiplying month by 30 (but could lose precision).
            step_length = declarative_cursor.get_step()

            return DeclarativeCursorAttributes(
                cursor_field=CursorField(declarative_cursor.cursor_field.eval(config=config)),
                datetime_format=declarative_cursor.datetime_format,
                slice_boundary_fields=slice_boundary_fields,
                start=start_date,
                end_provider=end_date_provider,
                slice_range=step_length,
                lookback_window=parse_duration(declarative_cursor.lookback_window) if declarative_cursor.lookback_window else None,
                cursor_granularity=parse_duration(declarative_cursor.cursor_granularity) if declarative_cursor.cursor_granularity else None,
            )
        return None

    @staticmethod
    def _get_cursor(stream: DeclarativeStream) -> Optional[DeclarativeCursor]:
        """
        Returns the low-code cursor component of a stream if it is concurrent compatible. Otherwise, returns None.
        """
        if not stream.supports_incremental:
            return None

        if isinstance(stream.retriever, SimpleRetriever):
            return stream.retriever.cursor

        return None

    @staticmethod
    def _select_streams(streams: List[AbstractStream], configured_catalog: ConfiguredAirbyteCatalog) -> List[AbstractStream]:
        stream_name_to_instance: Mapping[str, AbstractStream] = {s.name: s for s in streams}
        abstract_streams: List[AbstractStream] = []
        for configured_stream in configured_catalog.streams:
            stream_instance = stream_name_to_instance.get(configured_stream.stream.name)
            if stream_instance:
                abstract_streams.append(stream_instance)

        return abstract_streams

    @staticmethod
    def _remove_concurrent_streams_from_catalog(
        catalog: ConfiguredAirbyteCatalog,
        concurrent_stream_names: set[str],
    ) -> ConfiguredAirbyteCatalog:
        return ConfiguredAirbyteCatalog(streams=[stream for stream in catalog.streams if stream.stream.name not in concurrent_stream_names])

    # def _concurrency_level(self, config: Mapping[str, Any]) -> int:
    #     concurrency_level_definition = self._source_config["concurrency_level"]
    #     concurrency_level = self._constructor.create_component(
    #         model_type=ConcurrencyLevelModel,
    #         component_definition=concurrency_level_definition,
    #         config=config,
    #         emit_connector_builder_messages=self._emit_connector_builder_messages,
    #     )
    #
    #     if isinstance(concurrency_level, ConcurrencyLevel):
    #         return concurrency_level.get_concurrency_level()
    #     else:
    #         raise ValueError(f"Expected to generate a ConcurrencyLevel component, but received {concurrency_level.__class__}")
