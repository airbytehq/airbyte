#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent
import logging
import time
from abc import ABC
from concurrent.futures import Future
from queue import Queue
from typing import Any, Callable, Dict, Iterator, List, Mapping, MutableMapping, Optional, Union

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
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.concurrent_source.stream_complete_sentinel import StreamCompleteSentinel
from airbyte_cdk.sources.concurrent_source.stream_reader import StreamReader
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PARTITIONS_GENERATED_SENTINEL, PartitionCompleteSentinel
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.sources.utils.schema_helpers import split_config
from airbyte_cdk.utils.event_timing import MultiEventTimer, create_timer
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message


class ConcurrentSource(AbstractSource, ABC):
    def __init__(self, max_workers, timeout_in_seconds, message_repository=InMemoryMessageRepository(), **kwargs):
        super().__init__(**kwargs)
        self._max_workers = max_workers
        self._timeout_seconds = timeout_in_seconds
        self._stream_read_threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool")
        self._message_repository = message_repository

    @property
    def message_repository(self):
        return self._message_repository

    # FIXME: This probably deserves a nicer interface with an adapter
    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[Union[List[AirbyteStateMessage], MutableMapping[str, Any]]] = None,
    ) -> Iterator[AirbyteMessage]:
        logger.info(f"Starting syncing {self.name}")
        # yield from super().read(logger, config, catalog, state)
        futures: List[Future[Any]] = []
        queue: Queue = Queue()
        partition_generator = PartitionEnqueuer(queue)
        partition_reader = PartitionReader(queue)
        SENTINEL = object
        stream_reader = StreamReader(queue, SENTINEL, self._message_repository, logger)
        partitions_to_done: Dict[Partition, bool] = {}
        config, internal_config = split_config(config)
        # TODO assert all streams exist in the connector
        # get the streams once in case the connector needs to make any queries to generate them
        stream_instances: Mapping[str, AbstractStream] = {s.name: s for s in self._streams_as_abstract_streams(config)}
        # FIXME need to do something with state messages?
        # if not, delete next line
        state_manager = ConnectorStateManager(stream_instance_map=stream_instances, state=state)
        max_number_of_partition_generator_in_progress = 1
        self._stream_to_instance_map = stream_instances

        stream_instances_to_read_from = []
        timer = MultiEventTimer(self.name)
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
                # self._apply_log_level_to_stream_logger(logger, stream_instance)
                stream_availability = stream_instance.check_availability()
                if not stream_availability.is_available():
                    logger.warning(
                        f"Skipped syncing stream '{stream_instance.name}' because it was unavailable. {stream_availability.message()}"
                    )
                    continue
                timer.start_event(configured_stream.stream.name, f"Syncing stream {configured_stream.stream.name}")
                stream_instances_to_read_from.append(stream_instance)
        # for stream in stream_instances_to_read_from:
        #     # print(f"submitting task for stream {stream.name}")
        #     self._submit_task(futures, stream_reader.read_from_stream, stream)

        partition_generator_running = []
        partition_generators = [stream._stream_partition_generator for stream in stream_instances_to_read_from]
        print(f"partition_generators: {partition_generators}")
        while len(partition_generator_running) < max_number_of_partition_generator_in_progress:
            stream_partition_generator = partition_generators.pop(0)
            self._submit_task(futures, partition_generator.generate_partitions, stream_partition_generator)
            partition_generator_running.append(stream_partition_generator)

        # FIXME: I added this for one of the scenarios, but I'm not sure what the issue is...
        # time.sleep(0.5)

        total_records_counter = 0
        streams_in_progress = {stream for stream in stream_instances_to_read_from}
        while airbyte_message_or_record_or_exception := queue.get(block=True, timeout=self._timeout_seconds):
            if isinstance(airbyte_message_or_record_or_exception, Exception):
                # An exception was raised while processing the stream
                # Stop the threadpool and raise it
                # print(f"received exception {airbyte_message_or_record_or_exception}")
                # print(f"{stream_done_counter} out of {len(stream_instances_to_read_from)} left.")
                self._stream_read_threadpool.shutdown(wait=False, cancel_futures=True)
                for stream in streams_in_progress:
                    logger.info(f"Marking stream {stream.name} as STOPPED")
                    self._update_timer(stream, timer, logger)
                    yield stream_status_as_airbyte_message(
                        stream.name, stream.as_airbyte_stream().namespace, AirbyteStreamStatus.INCOMPLETE
                    )
                raise airbyte_message_or_record_or_exception

            elif isinstance(airbyte_message_or_record_or_exception, PartitionGenerationCompletedSentinel):
                partition_generator_running.remove(airbyte_message_or_record_or_exception.partition_generator)
                if partition_generators:
                    stream_partition_generator = partition_generators.pop(0)
                    self._submit_task(futures, partition_generator.generate_partitions, stream_partition_generator)
                    partition_generator_running.append(stream_partition_generator)

            elif isinstance(airbyte_message_or_record_or_exception, StreamCompleteSentinel):
                # FIXME This branch is immpossible
                # Update the map of stream -> done
                # print(f"done with a stream. {stream_done_counter} out of {len(stream_instances_to_read_from)}")
                stream = airbyte_message_or_record_or_exception.stream
                streams_in_progress.remove(stream)
                logger.info(f"Marking stream {stream.name} as STOPPED")
                self._update_timer(stream, timer, logger)
                yield stream_status_as_airbyte_message(stream.name, stream.as_airbyte_stream().namespace, AirbyteStreamStatus.COMPLETE)
                if not streams_in_progress:
                    # If all streams are done -> break
                    break
            elif isinstance(airbyte_message_or_record_or_exception, Partition):
                # A new partition was generated and must be processed
                # partitions_to_done[record_or_partition_or_exception] = False
                if self._slice_logger.should_log_slice_message(logger):
                    self._message_repository.emit_message(
                        self._slice_logger.create_slice_log_message(airbyte_message_or_record_or_exception.to_slice())
                    )
                self._submit_task(futures, partition_reader.process_partition, airbyte_message_or_record_or_exception)
            elif isinstance(airbyte_message_or_record_or_exception, PartitionCompleteSentinel):
                # All records for a partition were generated
                # if record_or_partition_or_exception.partition not in partitions_to_done:
                #     raise RuntimeError(
                #         f"Received sentinel for partition {record_or_partition_or_exception.partition} that was not in partitions. This is indicative of a bug in the CDK. Please contact support.partitions:\n{partitions_to_done}"
                #     )
                # self._cursor.close_partition(record_or_partition_or_exception.partition)
                partition = airbyte_message_or_record_or_exception.partition
                partitions_to_done[partition] = True
                # Fixme hacky
                self._stream_to_instance_map[partition._stream.name]._cursor.close_partition(partition)
            else:
                # record
                # Do not pass a transformer or a schema
                # AbstractStreams are expected to return data as they are expected.
                # Any transformation on the data should be done before reaching this point
                record = airbyte_message_or_record_or_exception
                message = stream_data_to_airbyte_message(
                    airbyte_message_or_record_or_exception.stream_name, airbyte_message_or_record_or_exception.data
                )
                yield message
                if message.type == MessageType.RECORD:
                    total_records_counter += 1
                # fixme hacky
                self._stream_to_instance_map[record.stream_name]._cursor.observe(record)
                yield from self._message_repository.consume_queue()
            if not partition_generator_running and all(partitions_to_done.values()):
                # All partitions were generated and process. We're done here
                break
        # TODO Some sort of error handling
        self._stream_read_threadpool.shutdown(wait=False, cancel_futures=True)
        # logger.info(timer.report())
        logger.info(f"Finished syncing {self.name}")

    def _update_timer(self, stream, timer, logger):
        timer.finish_event(stream.name)
        logger.info(f"Finished syncing {stream.name}")

    def _submit_task(self, futures: List[Future[Any]], function: Callable[..., Any], *args: Any) -> None:
        # Submit a task to the threadpool, waiting if there are too many pending tasks
        # self._wait_while_too_many_pending_futures(futures)
        futures.append(self._stream_read_threadpool.submit(function, *args))

    def _streams_as_abstract_streams(self, config) -> List[AbstractStream]:
        streams = self.streams(config)
        streams_as_abstract_streams = []
        for stream in streams:
            if isinstance(stream, StreamFacade):
                streams_as_abstract_streams.append(stream._abstract_stream)
            else:
                raise ValueError(f"Only StreamFacade is supported by ConcurrentSource. Got {stream}")
        return streams_as_abstract_streams
