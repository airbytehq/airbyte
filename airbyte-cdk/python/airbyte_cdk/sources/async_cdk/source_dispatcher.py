#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
import logging
from abc import ABC
from queue import Queue
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
)

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
)
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.sources.async_cdk.abstract_source_async import AsyncAbstractSource
from airbyte_cdk.sources.async_cdk.source_reader import Sentinel, SourceReader
from airbyte_cdk.sources.async_cdk.streams.core_async import AsyncStream
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, split_config
from airbyte_cdk.utils.event_timing import create_timer
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_cdk.utils.stream_status_utils import (
    as_airbyte_message as stream_status_as_airbyte_message,
)

DEFAULT_QUEUE_SIZE = 10000
DEFAULT_SESSION_LIMIT = 10000
DEFAULT_TIMEOUT = None


class SourceDispatcher(AbstractSource, ABC):
    """
    Abstract base class for an Airbyte Source that can dispatch to an async source.
    """

    def __init__(self, async_source: AsyncAbstractSource):
        self.async_source = async_source
        self.queue = Queue(DEFAULT_QUEUE_SIZE)
        self.session_limit = DEFAULT_SESSION_LIMIT

    def check_connection(
        self, logger: logging.Logger, config: Mapping[str, Any]
    ) -> Tuple[bool, Optional[Any]]:
        """
        Run the async_source's `check_connection` method on the event loop.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self.async_source.check_connection(logger, config)
        )

    def streams(self, config: Mapping[str, Any]) -> List[AsyncStream]:
        """
        Run the async_source's `streams` method on the event loop.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.async_source.streams(config))

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        """
        Run the async_source's `spec` method.
        """
        return self.async_source.spec(logger)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[
            Union[List[AirbyteStateMessage], MutableMapping[str, Any]]
        ] = None,
    ) -> Iterator[AirbyteMessage]:
        """
        Run the async_source's `read_streams` method and yield its results.

        """
        logger.info(f"Starting syncing {self.name}")
        config, internal_config = split_config(config)
        stream_instances: Mapping[str, AsyncStream] = {
            s.name: s for s in self.streams(config)
        }
        state_manager = ConnectorStateManager(
            stream_instance_map=stream_instances, state=state
        )
        self._stream_to_instance_map = stream_instances
        self._assert_streams(catalog, stream_instances)

        n_records = 0
        with create_timer(self.name) as timer:
            for record in self._do_read(
                catalog, stream_instances, timer, logger, state_manager, internal_config
            ):
                n_records += 1
                yield record

        print(f"_______________________-ASYNCIO SOURCE N RECORDS == {n_records}")
        logger.info(f"Finished syncing {self.name}")

    def _do_read(
        self,
        catalog: ConfiguredAirbyteCatalog,
        stream_instances: Dict[str, AsyncStream],
        timer: Any,
        logger: logging.Logger,
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ):
        streams_in_progress_sentinels = {
            s.stream.name: Sentinel(s.stream.name)
            for s in catalog.streams
            if s.stream.name in stream_instances
        }
        if not streams_in_progress_sentinels:
            return
        self.reader = SourceReader(
            logger,
            self.queue,
            streams_in_progress_sentinels,
            self._read_streams,
            catalog,
            stream_instances,
            timer,
            logger,
            state_manager,
            internal_config,
        )
        for record in self.reader:
            yield record

        for record in self.reader.drain():
            if isinstance(record, Exception):
                raise record
            yield record

    def _assert_streams(
        self,
        catalog: ConfiguredAirbyteCatalog,
        stream_instances: Dict[str, AsyncStream],
    ):
        for configured_stream in catalog.streams:
            stream_instance = stream_instances.get(configured_stream.stream.name)
            if not stream_instance:
                if not self.async_source.raise_exception_on_missing_stream:
                    return
                raise KeyError(
                    f"The stream {configured_stream.stream.name} no longer exists in the configuration. "
                    f"Refresh the schema in replication settings and remove this stream from future sync attempts."
                )

    async def _read_streams(
        self,
        catalog: ConfiguredAirbyteCatalog,
        stream_instances: Dict[str, AsyncStream],
        timer: Any,
        logger: logging.Logger,
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ):
        pending_tasks = set()
        n_started, n_streams = 0, len(catalog.streams)
        streams_iterator = iter(catalog.streams)
        exceptions = False

        while (pending_tasks or n_started < n_streams) and not exceptions:
            while len(pending_tasks) < self.session_limit and (
                configured_stream := next(streams_iterator, None)
            ):
                if configured_stream is None:
                    break
                stream_instance = stream_instances.get(configured_stream.stream.name)
                stream = stream_instances.get(configured_stream.stream.name)
                self.reader.sessions[
                    configured_stream.stream.name
                ] = await stream.ensure_session()
                pending_tasks.add(
                    asyncio.create_task(
                        self._do_async_read_stream(
                            configured_stream,
                            stream_instance,
                            timer,
                            logger,
                            state_manager,
                            internal_config,
                        )
                    )
                )
                n_started += 1

            done, pending_tasks = await asyncio.wait(
                pending_tasks, return_when=asyncio.FIRST_COMPLETED
            )

            for task in done:
                if exc := task.exception():
                    for remaining_task in pending_tasks:
                        await remaining_task.cancel()
                    self.queue.put(exc)
                    exceptions = True

    async def _do_async_read_stream(
        self,
        configured_stream: ConfiguredAirbyteStream,
        stream_instance: AsyncStream,
        timer: Any,
        logger: logging.Logger,
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ):
        try:
            await self._async_read_stream(
                configured_stream,
                stream_instance,
                timer,
                logger,
                state_manager,
                internal_config,
            )
        finally:
            self.queue.put(Sentinel(configured_stream.stream.name))

    async def _async_read_stream(
        self,
        configured_stream: ConfiguredAirbyteStream,
        stream_instance: AsyncStream,
        timer: Any,
        logger: logging.Logger,
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ):
        try:
            timer.start_event(f"Syncing stream {configured_stream.stream.name}")
            stream_is_available, reason = await stream_instance.check_availability(
                logger, self.async_source
            )
            if not stream_is_available:
                logger.warning(
                    f"Skipped syncing stream '{stream_instance.name}' because it was unavailable. {reason}"
                )
                return
            logger.info(f"Marking stream {configured_stream.stream.name} as STARTED")
            self.queue.put(
                stream_status_as_airbyte_message(
                    configured_stream.stream, AirbyteStreamStatus.STARTED
                )
            )
            async for record in self.async_source.read_stream(
                logger=logger,
                stream_instance=stream_instance,
                configured_stream=configured_stream,
                state_manager=state_manager,
                internal_config=internal_config,
            ):
                self.queue.put(record)
            logger.info(f"Marking stream {configured_stream.stream.name} as STOPPED")
            self.queue.put(
                stream_status_as_airbyte_message(
                    configured_stream.stream, AirbyteStreamStatus.COMPLETE
                )
            )
        except AirbyteTracedException as e:
            self.queue.put(
                stream_status_as_airbyte_message(
                    configured_stream.stream, AirbyteStreamStatus.INCOMPLETE
                )
            )
            raise e
        except Exception as e:
            for message in self._emit_queued_messages():
                self.queue.put(message)
            logger.exception(
                f"Encountered an exception while reading stream {configured_stream.stream.name}"
            )
            logger.info(f"Marking stream {configured_stream.stream.name} as STOPPED")
            self.queue.put(
                stream_status_as_airbyte_message(
                    configured_stream.stream, AirbyteStreamStatus.INCOMPLETE
                )
            )
            display_message = stream_instance.get_error_display_message(e)
            if display_message:
                raise AirbyteTracedException.from_exception(e, message=display_message)
            else:
                raise e
        finally:
            timer.finish_event()
            logger.info(f"Finished syncing {configured_stream.stream.name}")
            # logger.info(timer.report())  # TODO - this is causing scenario-based test failures
