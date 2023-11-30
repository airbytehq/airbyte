#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Status,
    SyncMode,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.source import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http.http import HttpStream
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, split_config
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger, SliceLogger
from airbyte_cdk.utils.event_timing import create_timer
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


class AbstractSource(Source, ABC):
    """
    Abstract base class for an Airbyte Source. Consumers should implement any abstract methods
    in this class to create an Airbyte Specification compliant Source.
    """

    @abstractmethod
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        :param logger: source logger
        :param config: The user-provided configuration as specified by the source's spec.
          This usually contains information required to check connection e.g. tokens, secrets and keys etc.
        :return: A tuple of (boolean, error). If boolean is true, then the connection check is successful
          and we can connect to the underlying data source using the provided configuration.
          Otherwise, the input config cannot be used to connect to the underlying data source,
          and the "error" object should describe what went wrong.
          The error object will be cast to string to display the problem to the user.
        """

    @abstractmethod
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: The user-provided configuration as specified by the source's spec.
        Any stream construction related operation should happen here.
        :return: A list of the streams in this source connector.
        """

    # Stream name to instance map for applying output object transformation
    _stream_to_instance_map: Dict[str, Stream] = {}
    _slice_logger: SliceLogger = DebugSliceLogger()

    @property
    def name(self) -> str:
        """Source name"""
        return self.__class__.__name__

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Implements the Discover operation from the Airbyte Specification.
        See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#discover.
        """
        streams = [stream.as_airbyte_stream() for stream in self.streams(config=config)]
        return AirbyteCatalog(streams=streams)

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Implements the Check Connection operation from the Airbyte Specification.
        See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#check.
        """
        check_succeeded, error = self.check_connection(logger, config)
        if not check_succeeded:
            return AirbyteConnectionStatus(status=Status.FAILED, message=repr(error))
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[Union[List[AirbyteStateMessage], MutableMapping[str, Any]]] = None,
    ) -> Iterator[AirbyteMessage]:
        """Implements the Read operation from the Airbyte Specification. See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/."""
        logger.info(f"Starting syncing {self.name}")
        config, internal_config = split_config(config)
        # TODO assert all streams exist in the connector
        # get the streams once in case the connector needs to make any queries to generate them
        stream_instances = {s.name: s for s in self.streams(config)}
        state_manager = ConnectorStateManager(stream_instance_map=stream_instances, state=state)
        self._stream_to_instance_map = stream_instances
        with create_timer(self.name) as timer:
            for configured_stream in catalog.streams:
                stream_instance = stream_instances.get(configured_stream.stream.name)
                if not stream_instance:
                    if not self.raise_exception_on_missing_stream:
                        continue
                    raise KeyError(
                        f"The stream {configured_stream.stream.name} no longer exists in the configuration. "
                        f"Refresh the schema in replication settings and remove this stream from future sync attempts."
                    )

                try:
                    timer.start_event(f"Syncing stream {configured_stream.stream.name}")
                    stream_is_available, reason = stream_instance.check_availability(logger, self)
                    if not stream_is_available:
                        logger.warning(f"Skipped syncing stream '{stream_instance.name}' because it was unavailable. {reason}")
                        continue
                    logger.info(f"Marking stream {configured_stream.stream.name} as STARTED")
                    yield stream_status_as_airbyte_message(configured_stream.stream, AirbyteStreamStatus.STARTED)
                    yield from self._read_stream(
                        logger=logger,
                        stream_instance=stream_instance,
                        configured_stream=configured_stream,
                        state_manager=state_manager,
                        internal_config=internal_config,
                    )
                    logger.info(f"Marking stream {configured_stream.stream.name} as STOPPED")
                    yield stream_status_as_airbyte_message(configured_stream.stream, AirbyteStreamStatus.COMPLETE)
                except AirbyteTracedException as e:
                    yield stream_status_as_airbyte_message(configured_stream.stream, AirbyteStreamStatus.INCOMPLETE)
                    raise e
                except Exception as e:
                    yield from self._emit_queued_messages()
                    logger.exception(f"Encountered an exception while reading stream {configured_stream.stream.name}")
                    logger.info(f"Marking stream {configured_stream.stream.name} as STOPPED")
                    yield stream_status_as_airbyte_message(configured_stream.stream, AirbyteStreamStatus.INCOMPLETE)
                    display_message = stream_instance.get_error_display_message(e)
                    if display_message:
                        raise AirbyteTracedException.from_exception(e, message=display_message) from e
                    raise e
                finally:
                    timer.finish_event()
                    logger.info(f"Finished syncing {configured_stream.stream.name}")
                    logger.info(timer.report())

        logger.info(f"Finished syncing {self.name}")

    @property
    def raise_exception_on_missing_stream(self) -> bool:
        return True

    @property
    def per_stream_state_enabled(self) -> bool:
        return True

    def _read_stream(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        if internal_config.page_size and isinstance(stream_instance, HttpStream):
            logger.info(f"Setting page size for {stream_instance.name} to {internal_config.page_size}")
            stream_instance.page_size = internal_config.page_size
        logger.debug(
            f"Syncing configured stream: {configured_stream.stream.name}",
            extra={
                "sync_mode": configured_stream.sync_mode,
                "primary_key": configured_stream.primary_key,
                "cursor_field": configured_stream.cursor_field,
            },
        )
        stream_instance.log_stream_sync_configuration()

        use_incremental = configured_stream.sync_mode == SyncMode.incremental and stream_instance.supports_incremental
        if use_incremental:
            record_iterator = self._read_incremental(
                logger,
                stream_instance,
                configured_stream,
                state_manager,
                internal_config,
            )
        else:
            record_iterator = self._read_full_refresh(logger, stream_instance, configured_stream, internal_config)

        record_counter = 0
        stream_name = configured_stream.stream.name
        logger.info(f"Syncing stream: {stream_name} ")
        for record in record_iterator:
            if record.type == MessageType.RECORD:
                record_counter += 1
                if record_counter == 1:
                    logger.info(f"Marking stream {stream_name} as RUNNING")
                    # If we just read the first record of the stream, emit the transition to the RUNNING state
                    yield stream_status_as_airbyte_message(configured_stream.stream, AirbyteStreamStatus.RUNNING)
            yield from self._emit_queued_messages()
            yield record

        logger.info(f"Read {record_counter} records from {stream_name} stream")

    def _read_incremental(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        """Read stream using incremental algorithm

        :param logger:
        :param stream_instance:
        :param configured_stream:
        :param state_manager:
        :param internal_config:
        :return:
        """
        stream_name = configured_stream.stream.name
        stream_state = state_manager.get_stream_state(stream_name, stream_instance.namespace)

        if stream_state and "state" in dir(stream_instance):
            stream_instance.state = stream_state  # type: ignore # we check that state in the dir(stream_instance)
            logger.info(f"Setting state of {self.name} stream to {stream_state}")

        for record_data_or_message in stream_instance.read_incremental(
            configured_stream.cursor_field,
            logger,
            self._slice_logger,
            stream_state,
            state_manager,
            self.per_stream_state_enabled,
            internal_config,
        ):
            yield self._get_message(record_data_or_message, stream_instance)

    def _emit_queued_messages(self) -> Iterable[AirbyteMessage]:
        if self.message_repository:
            yield from self.message_repository.consume_queue()
        return

    def _read_full_refresh(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        total_records_counter = 0
        for record_data_or_message in stream_instance.read_full_refresh(configured_stream.cursor_field, logger, self._slice_logger):
            message = self._get_message(record_data_or_message, stream_instance)
            yield message
            if message.type == MessageType.RECORD:
                total_records_counter += 1
                if internal_config.is_limit_reached(total_records_counter):
                    return

    def _get_message(self, record_data_or_message: Union[StreamData, AirbyteMessage], stream: Stream) -> AirbyteMessage:
        """
        Converts the input to an AirbyteMessage if it is a StreamData. Returns the input as is if it is already an AirbyteMessage
        """
        if isinstance(record_data_or_message, AirbyteMessage):
            return record_data_or_message
        else:
            return stream_data_to_airbyte_message(stream.name, record_data_or_message, stream.transformer, stream.get_json_schema())

    @property
    def message_repository(self) -> Union[None, MessageRepository]:
        return None
