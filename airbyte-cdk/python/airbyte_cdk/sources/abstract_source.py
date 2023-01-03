#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Status,
    SyncMode,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.source import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http.http import HttpStream
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, split_config
from airbyte_cdk.utils.event_timing import create_timer
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
        try:
            check_succeeded, error = self.check_connection(logger, config)
            if not check_succeeded:
                return AirbyteConnectionStatus(status=Status.FAILED, message=repr(error))
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=repr(e))

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
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
                    raise KeyError(
                        f"The requested stream {configured_stream.stream.name} was not found in the source."
                        f" Available streams: {stream_instances.keys()}"
                    )
                try:
                    timer.start_event(f"Syncing stream {configured_stream.stream.name}")
                    yield from self._read_stream(
                        logger=logger,
                        stream_instance=stream_instance,
                        configured_stream=configured_stream,
                        state_manager=state_manager,
                        internal_config=internal_config,
                    )
                except AirbyteTracedException as e:
                    raise e
                except Exception as e:
                    logger.exception(f"Encountered an exception while reading stream {configured_stream.stream.name}")
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
        self._apply_log_level_to_stream_logger(logger, stream_instance)
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
        logger.debug(
            f"Syncing stream instance: {stream_instance.name}",
            extra={
                "primary_key": stream_instance.primary_key,
                "cursor_field": stream_instance.cursor_field,
            },
        )

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
            yield record

        logger.info(f"Read {record_counter} records from {stream_name} stream")

    @staticmethod
    def _limit_reached(internal_config: InternalConfig, records_counter: int) -> bool:
        """
        Check if record count reached liimt set by internal config.
        :param internal_config - internal CDK configuration separated from user defined config
        :records_counter - number of records already red
        :return True if limit reached, False otherwise
        """
        if internal_config.limit:
            if records_counter >= internal_config.limit:
                return True
        return False

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
            stream_instance.state = stream_state
            logger.info(f"Setting state of {stream_name} stream to {stream_state}")

        slices = stream_instance.stream_slices(
            cursor_field=configured_stream.cursor_field,
            sync_mode=SyncMode.incremental,
            stream_state=stream_state,
        )
        logger.debug(f"Processing stream slices for {stream_name} (sync_mode: incremental)", extra={"stream_slices": slices})

        total_records_counter = 0
        has_slices = False
        for _slice in slices:
            has_slices = True
            logger.debug("Processing stream slice", extra={"slice": _slice})
            records = stream_instance.read_records(
                sync_mode=SyncMode.incremental,
                stream_slice=_slice,
                stream_state=stream_state,
                cursor_field=configured_stream.cursor_field or None,
            )
            record_counter = 0
            for message_counter, record_data_or_message in enumerate(records, start=1):
                message = self._get_message(record_data_or_message, stream_instance)
                yield message
                if message.type == MessageType.RECORD:
                    record = message.record
                    stream_state = stream_instance.get_updated_state(stream_state, record.data)
                    checkpoint_interval = stream_instance.state_checkpoint_interval
                    record_counter += 1
                    if checkpoint_interval and record_counter % checkpoint_interval == 0:
                        yield self._checkpoint_state(stream_instance, stream_state, state_manager)

                    total_records_counter += 1
                    # This functionality should ideally live outside of this method
                    # but since state is managed inside this method, we keep track
                    # of it here.
                    if self._limit_reached(internal_config, total_records_counter):
                        # Break from slice loop to save state and exit from _read_incremental function.
                        break

            yield self._checkpoint_state(stream_instance, stream_state, state_manager)
            if self._limit_reached(internal_config, total_records_counter):
                return

        if not has_slices:
            # Safety net to ensure we always emit at least one state message even if there are no slices
            checkpoint = self._checkpoint_state(stream_instance, stream_state, state_manager)
            yield checkpoint

    def _read_full_refresh(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh, cursor_field=configured_stream.cursor_field)
        logger.debug(
            f"Processing stream slices for {configured_stream.stream.name} (sync_mode: full_refresh)", extra={"stream_slices": slices}
        )
        total_records_counter = 0
        for _slice in slices:
            logger.debug("Processing stream slice", extra={"slice": _slice})
            record_data_or_messages = stream_instance.read_records(
                stream_slice=_slice,
                sync_mode=SyncMode.full_refresh,
                cursor_field=configured_stream.cursor_field,
            )
            for record_data_or_message in record_data_or_messages:
                message = self._get_message(record_data_or_message, stream_instance)
                yield message
                if message.type == MessageType.RECORD:
                    total_records_counter += 1
                    if self._limit_reached(internal_config, total_records_counter):
                        return

    def _checkpoint_state(self, stream: Stream, stream_state, state_manager: ConnectorStateManager):
        # First attempt to retrieve the current state using the stream's state property. We receive an AttributeError if the state
        # property is not implemented by the stream instance and as a fallback, use the stream_state retrieved from the stream
        # instance's deprecated get_updated_state() method.
        try:
            state_manager.update_state_for_stream(stream.name, stream.namespace, stream.state)

        except AttributeError:
            state_manager.update_state_for_stream(stream.name, stream.namespace, stream_state)
        return state_manager.create_state_message(stream.name, stream.namespace, send_per_stream_state=self.per_stream_state_enabled)

    @staticmethod
    def _apply_log_level_to_stream_logger(logger: logging.Logger, stream_instance: Stream):
        """
        Necessary because we use different loggers at the source and stream levels. We must
        apply the source's log level to each stream's logger.
        """
        if hasattr(logger, "level"):
            stream_instance.logger.setLevel(logger.level)

    def _get_message(self, record_data_or_message: Union[StreamData, AirbyteMessage], stream: Stream):
        """
        Converts the input to an AirbyteMessage if it is a StreamData. Returns the input as is if it is already an AirbyteMessage
        """
        if isinstance(record_data_or_message, AirbyteMessage):
            return record_data_or_message
        else:
            return stream_data_to_airbyte_message(stream.name, record_data_or_message, stream.transformer, stream.get_json_schema())
