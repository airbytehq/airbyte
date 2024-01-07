#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from typing import (
    Any,
    AsyncGenerator,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
)

from airbyte_cdk.models import (
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
from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.sources.async_cdk.streams.core_async import AsyncStream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http.http import HttpStream
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.utils.stream_status_utils import (
    as_airbyte_message as stream_status_as_airbyte_message,
)


class AsyncAbstractSource(AbstractSource, ABC):
    """
    Abstract base class for an Airbyte Source. Consumers should implement any abstract methods
    in this class to create an Airbyte Specification compliant Source.
    """

    @abstractmethod
    async def check_connection(
        self, logger: logging.Logger, config: Mapping[str, Any]
    ) -> Tuple[bool, Optional[Any]]:
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

    async def check(
        self, logger: logging.Logger, config: Mapping[str, Any]
    ) -> AirbyteConnectionStatus:
        """Implements the Check Connection operation from the Airbyte Specification.
        See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#check.
        """
        check_succeeded, error = await self.check_connection(logger, config)
        if not check_succeeded:
            return AirbyteConnectionStatus(status=Status.FAILED, message=repr(error))
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    @abstractmethod
    async def streams(self, config: Mapping[str, Any]) -> List[AsyncStream]:
        """
        :param config: The user-provided configuration as specified by the source's spec.
        Any stream construction related operation should happen here.
        :return: A list of the streams in this source connector.
        """

    async def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[
            Union[List[AirbyteStateMessage], MutableMapping[str, Any]]
        ] = None,
    ) -> Iterator[AirbyteMessage]:
        """
        Implements the Read operation from the Airbyte Specification. See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/.

        This method is not used when the AsyncSource is used in conjunction with the AsyncSourceDispatcher.
        """
        ...

    async def read_stream(
        self,
        logger: logging.Logger,
        stream_instance: AsyncStream,
        configured_stream: ConfiguredAirbyteStream,
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ) -> AsyncGenerator[AirbyteMessage, None]:
        if internal_config.page_size and isinstance(stream_instance, HttpStream):
            logger.info(
                f"Setting page size for {stream_instance.name} to {internal_config.page_size}"
            )
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

        use_incremental = (
            configured_stream.sync_mode == SyncMode.incremental
            and stream_instance.supports_incremental
        )
        if use_incremental:
            record_iterator = self._read_incremental(
                logger,
                stream_instance,
                configured_stream,
                state_manager,
                internal_config,
            )
        else:
            record_iterator = self._read_full_refresh(
                logger, stream_instance, configured_stream, internal_config
            )

        record_counter = 0
        stream_name = configured_stream.stream.name
        logger.info(f"Syncing stream: {stream_name} ")
        async for record in record_iterator:
            if record.type == MessageType.RECORD:
                record_counter += 1
                if record_counter == 1:
                    logger.info(f"Marking stream {stream_name} as RUNNING")
                    # If we just read the first record of the stream, emit the transition to the RUNNING state
                    yield stream_status_as_airbyte_message(
                        configured_stream.stream, AirbyteStreamStatus.RUNNING
                    )
            for message in self._emit_queued_messages():
                yield message
            yield record

        logger.info(f"Read {record_counter} records from {stream_name} stream")

    async def _read_incremental(
        self,
        logger: logging.Logger,
        stream_instance: AsyncStream,
        configured_stream: ConfiguredAirbyteStream,
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ) -> AsyncGenerator[AirbyteMessage, None]:
        """Read stream using incremental algorithm

        :param logger:
        :param stream_instance:
        :param configured_stream:
        :param state_manager:
        :param internal_config:
        :return:
        """
        stream_name = configured_stream.stream.name
        stream_state = state_manager.get_stream_state(
            stream_name, stream_instance.namespace
        )

        if stream_state and "state" in dir(stream_instance):
            stream_instance.state = stream_state  # type: ignore # we check that state in the dir(stream_instance)
            logger.info(f"Setting state of {self.name} stream to {stream_state}")

        async for record_data_or_message in stream_instance.read_incremental(
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

    async def _read_full_refresh(
        self,
        logger: logging.Logger,
        stream_instance: AsyncStream,
        configured_stream: ConfiguredAirbyteStream,
        internal_config: InternalConfig,
    ) -> AsyncGenerator[AirbyteMessage, None]:
        total_records_counter = 0
        async for record_data_or_message in stream_instance.read_full_refresh(
            configured_stream.cursor_field, logger, self._slice_logger
        ):
            message = self._get_message(record_data_or_message, stream_instance)
            yield message
            if message.type == MessageType.RECORD:
                total_records_counter += 1
                if internal_config.is_limit_reached(total_records_counter):
                    return

    def _get_message(
        self,
        record_data_or_message: Union[StreamData, AirbyteMessage],
        stream: AsyncStream,
    ) -> AirbyteMessage:
        """
        Converts the input to an AirbyteMessage if it is a StreamData. Returns the input as is if it is already an AirbyteMessage
        """
        if isinstance(record_data_or_message, AirbyteMessage):
            return record_data_or_message
        else:
            return stream_data_to_airbyte_message(
                stream.name,
                record_data_or_message,
                stream.transformer,
                stream.get_json_schema(),
            )
