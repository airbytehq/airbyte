#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent
import logging
from abc import ABC
from concurrent.futures import Future
from queue import Queue
from typing import Any, Callable, Iterator, List, Mapping, MutableMapping, Optional, Union

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
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.concurrent_source.stream_reader import StreamReader
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.utils.schema_helpers import split_config
from airbyte_cdk.utils.event_timing import create_timer


class ConcurrentSource(AbstractSource, ABC):
    def __init__(self, max_workers, timeout_in_seconds, **kwargs):
        super().__init__(**kwargs)
        self._max_workers = max_workers
        self._timeout_seconds = timeout_in_seconds
        self._threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool")

    # FIXME: This probably deserves a nicer interface with an adapter
    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[Union[List[AirbyteStateMessage], MutableMapping[str, Any]]] = None,
    ) -> Iterator[AirbyteMessage]:
        # yield from super().read(logger, config, catalog, state)
        futures: List[Future[Any]] = []
        queue: Queue = Queue()
        SENTINEL = object
        stream_reader = StreamReader(queue, SENTINEL)
        logger.info(f"Starting syncing {self.name}")
        config, internal_config = split_config(config)
        # TODO assert all streams exist in the connector
        # get the streams once in case the connector needs to make any queries to generate them
        stream_instances = {s.name: s for s in self.streams(config)}
        state_manager = ConnectorStateManager(stream_instance_map=stream_instances, state=state)
        self._stream_to_instance_map = stream_instances

        stream_instances_to_read_from = []
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
                else:
                    self._apply_log_level_to_stream_logger(logger, stream_instance)
                    timer.start_event(f"Syncing stream {configured_stream.stream.name}")
                    stream_is_available, reason = stream_instance.check_availability(logger, self)
                    if not stream_is_available:
                        logger.warning(f"Skipped syncing stream '{stream_instance.name}' because it was unavailable. {reason}")
                        continue
                    stream_instances_to_read_from.append(stream_instance)
            for stream in stream_instances_to_read_from:
                print(f"submitting task for stream {stream.name}")
                self._submit_task(futures, stream_reader.read_from_stream, stream)

            stop = False
            total_records_counter = 0
            stream_done_counter = 0
            while airbyte_message_or_record_or_exception := queue.get(block=True, timeout=self._timeout_seconds):
                if isinstance(airbyte_message_or_record_or_exception, Exception):
                    # An exception was raised while processing the stream
                    # Stop the threadpool and raise it
                    self._threadpool.shutdown(wait=False, cancel_futures=True)
                    raise airbyte_message_or_record_or_exception

                elif airbyte_message_or_record_or_exception == SENTINEL:
                    # Update the map of stream -> done
                    stream_done_counter += 1
                    print(f"done with a stream. {stream_done_counter} out of {len(stream_instances_to_read_from)}")
                    if stream_done_counter == len(stream_instances_to_read_from):
                        stop = True
                else:
                    message = self._get_message(airbyte_message_or_record_or_exception.data, stream_instance)
                    yield message
                    if message.type == MessageType.RECORD:
                        total_records_counter += 1
                if stop:
                    # If all streams are done -> break
                    break

    def _submit_task(self, futures: List[Future[Any]], function: Callable[..., Any], *args: Any) -> None:
        # Submit a task to the threadpool, waiting if there are too many pending tasks
        # self._wait_while_too_many_pending_futures(futures)
        futures.append(self._threadpool.submit(function, *args))
