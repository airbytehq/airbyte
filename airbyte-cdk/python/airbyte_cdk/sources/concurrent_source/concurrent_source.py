#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent
import logging
from abc import ABC
from concurrent.futures import Future
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from typing import Any, Callable, Dict, Iterator, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, AirbyteStreamStatus, ConfiguredAirbyteCatalog
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.sources.utils.schema_helpers import split_config
from airbyte_cdk.utils.event_timing import MultiEventTimer
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message


class Status(Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"


@dataclass
class PartitionReadStatus:
    partition: Partition
    partition_read_status: Status


@dataclass
class StreamReadStatus:
    stream: AbstractStream
    partition_generation_status: Status
    partition_read_statuses: List[PartitionReadStatus]


class ConcurrentSource(AbstractSource, ABC):
    def __init__(self, max_workers, timeout_in_seconds, message_repository=InMemoryMessageRepository(), **kwargs):
        super().__init__(**kwargs)
        self._max_workers = max_workers
        self._timeout_seconds = timeout_in_seconds
        self._threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool")
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
        config, internal_config = split_config(config)
        # TODO assert all streams exist in the connector
        # get the streams once in case the connector needs to make any queries to generate them
        stream_instances: Mapping[str, AbstractStream] = {s.name: s for s in self._streams_as_abstract_streams(config)}
        max_number_of_partition_generator_in_progress = max(1, self._max_workers // 2)
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
                # FIXME: need to enable debug logging somehow
                # self._apply_log_level_to_stream_logger(logger, stream_instance)
                stream_availability = stream_instance.check_availability()
                if not stream_availability.is_available():
                    logger.warning(
                        f"Skipped syncing stream '{stream_instance.name}' because it was unavailable. {stream_availability.message()}"
                    )
                    continue
                timer.start_event(configured_stream.stream.name, f"Syncing stream {configured_stream.stream.name}")
                stream_instances_to_read_from.append(stream_instance)

        partition_generator_running = []
        partition_generators = [stream._stream_partition_generator for stream in stream_instances_to_read_from]
        streams_to_partitions_to_done: Dict[str, Dict[Partition, bool]] = {}
        record_counter = {}
        for stream in stream_instances_to_read_from:
            streams_to_partitions_to_done[stream.name] = {}
            record_counter[stream.name] = 0
        while len(partition_generator_running) < max_number_of_partition_generator_in_progress:
            yield self._start_next_partition_generator(
                partition_generators, futures, partition_generator_running, partition_generator, logger
            )

        while airbyte_message_or_record_or_exception := queue.get(block=True, timeout=self._timeout_seconds):
            if isinstance(airbyte_message_or_record_or_exception, Exception):
                # An exception was raised while processing the stream
                # Stop the threadpool and raise it
                yield from self._stop_streams(streams_to_partitions_to_done, stream_instances, timer, logger)
                raise airbyte_message_or_record_or_exception

            elif isinstance(airbyte_message_or_record_or_exception, PartitionGenerationCompletedSentinel):
                yield from self._handle_partition_generation_completed(
                    airbyte_message_or_record_or_exception,
                    partition_generator_running,
                    partition_generators,
                    partition_generator,
                    futures,
                    logger,
                    streams_to_partitions_to_done,
                    stream_instances,
                    record_counter,
                    timer,
                )

            elif isinstance(airbyte_message_or_record_or_exception, Partition):
                # A new partition was generated and must be processed
                self._handle_partition(
                    airbyte_message_or_record_or_exception, streams_to_partitions_to_done, futures, partition_reader, logger
                )
            elif isinstance(airbyte_message_or_record_or_exception, PartitionCompleteSentinel):
                # All records for a partition were generated
                partition = airbyte_message_or_record_or_exception.partition
                status_message = self._handle_partition_completed(
                    partition,
                    streams_to_partitions_to_done,
                    record_counter,
                    partition_generator_running,
                    stream_instances,
                    timer,
                    logger,
                )
                if status_message:
                    yield status_message
                # if all([all(partition_to_done.values()) for partition_to_done in streams_to_partitions_to_done.values()]):
                #     # If all streams are done -> break
                #     break
            else:
                # record
                yield from self._handle_record(airbyte_message_or_record_or_exception, record_counter, logger)
            if self._is_done(streams_to_partitions_to_done, partition_generators, partition_generator_running):
                # All partitions were generated and process. We're done here
                if all([f.done() for f in futures]) and queue.empty():
                    break
        # TODO Some sort of error handling
        self._threadpool.shutdown(wait=False, cancel_futures=True)
        logger.info(timer.report())
        logger.info(f"Finished syncing {self.name}")

    def _is_done(self, streams_to_partitions_to_done, partition_generators, partition_generator_running):
        return (
            not partition_generator_running
            and not partition_generators
            and all([all(partition_to_done.values()) for partition_to_done in streams_to_partitions_to_done.values()])
        )

    def _start_next_partition_generator(self, partition_generators, futures, partition_generator_running, partition_generator, logger):
        stream_partition_generator = partition_generators.pop(0)
        self._submit_task(futures, partition_generator.generate_partitions, stream_partition_generator)
        partition_generator_running.append(stream_partition_generator.stream_name())
        logger.info(f"Marking stream {stream_partition_generator.stream_name()} as STARTED")
        logger.info(f"Syncing stream: {stream_partition_generator.stream_name()} ")
        return stream_status_as_airbyte_message(
            # FIXME pass namespace
            stream_partition_generator.stream_name(),
            None,
            AirbyteStreamStatus.STARTED,
        )

    def _handle_record(self, record, record_counter, logger):
        # Do not pass a transformer or a schema
        # AbstractStreams are expected to return data as they are expected.
        # Any transformation on the data should be done before reaching this point
        message = stream_data_to_airbyte_message(record.stream_name, record.data)
        stream = self._stream_to_instance_map[record.stream_name]
        status_message = None
        if record_counter[stream.name] == 0:
            logger.info(f"Marking stream {stream.name} as RUNNING")

            status_message = stream_status_as_airbyte_message(
                stream.name, stream.as_airbyte_stream().namespace, AirbyteStreamStatus.RUNNING
            )
        if message.type == MessageType.RECORD:
            record_counter[stream.name] += 1
        # fixme hacky
        self._stream_to_instance_map[record.stream_name]._cursor.observe(record)
        if status_message:
            return [status_message, message] + list(self._message_repository.consume_queue())
        else:
            return [message] + list(self._message_repository.consume_queue())

    def _handle_partition(self, partition, streams_to_partitions_to_done, futures, partition_reader, logger):
        stream_name = partition.stream_name()
        streams_to_partitions_to_done[stream_name][partition] = False
        if self._slice_logger.should_log_slice_message(logger):
            self._message_repository.emit_message(self._slice_logger.create_slice_log_message(partition.to_slice()))
        self._submit_task(futures, partition_reader.process_partition, partition)

    def _handle_partition_generation_completed(
        self,
        sentinel,
        partition_generator_running,
        partition_generators,
        partition_generator,
        futures,
        logger,
        streams_to_partitions_to_done,
        stream_instances,
        record_counter,
        timer,
    ):
        stream_name = sentinel.partition_generator.stream_name()
        partition_generator_running.remove(sentinel.partition_generator.stream_name())
        ret = []
        if self._is_stream_done(stream_name, streams_to_partitions_to_done, partition_generator_running):
            ret.append(self._handle_stream_is_done(stream_name, stream_instances, record_counter, timer, logger))
        if partition_generators:
            ret.append(
                self._start_next_partition_generator(
                    partition_generators, futures, partition_generator_running, partition_generator, logger
                )
            )
        return ret

    def _handle_partition_completed(
        self,
        partition,
        streams_to_partitions_to_done,
        record_counter,
        partition_generator_running,
        stream_instances,
        timer,
        logger,
    ):
        stream_name = partition.stream_name()
        streams_to_partitions_to_done[stream_name][partition] = True
        # Fixme hacky
        self._stream_to_instance_map[stream_name]._cursor.close_partition(partition)
        if self._is_stream_done(stream_name, streams_to_partitions_to_done, partition_generator_running):
            # stream is done!
            return self._handle_stream_is_done(stream_name, stream_instances, record_counter, timer, logger)
        else:
            return None

    def _is_stream_done(self, stream_name, streams_to_partitions_to_done, partition_generator_running):
        return all(streams_to_partitions_to_done[stream_name].values()) and stream_name not in partition_generator_running

    def _handle_stream_is_done(self, stream_name, stream_instances, record_counter, timer, logger):
        logger.info(f"Read {record_counter[stream_name]} records from {stream_name} stream")
        logger.info(f"Marking stream {stream_name} as STOPPED")
        stream = stream_instances[stream_name]
        self._update_timer(stream, timer, logger)
        return stream_status_as_airbyte_message(stream.name, stream.as_airbyte_stream().namespace, AirbyteStreamStatus.COMPLETE)

    def _stop_streams(self, streams_to_partitions_to_done, stream_instances, timer, logger):
        self._threadpool.shutdown(wait=False, cancel_futures=True)
        for stream_name, partitions_to_done in streams_to_partitions_to_done.items():
            stream = stream_instances[stream_name]
            if not all(partitions_to_done.values()):
                logger.info(f"Marking stream {stream.name} as STOPPED")
                self._update_timer(stream, timer, logger)
                yield stream_status_as_airbyte_message(stream.name, stream.as_airbyte_stream().namespace, AirbyteStreamStatus.INCOMPLETE)

    def _update_timer(self, stream, timer, logger):
        timer.finish_event(stream.name)
        logger.info(f"Finished syncing {stream.name}")

    def _submit_task(self, futures: List[Future[Any]], function: Callable[..., Any], *args: Any) -> None:
        # Submit a task to the threadpool, waiting if there are too many pending tasks
        # self._wait_while_too_many_pending_futures(futures)
        futures.append(self._threadpool.submit(function, *args))

    def _streams_as_abstract_streams(self, config) -> List[AbstractStream]:
        streams = self.streams(config)
        streams_as_abstract_streams = []
        for stream in streams:
            if isinstance(stream, StreamFacade):
                streams_as_abstract_streams.append(stream._abstract_stream)
            else:
                raise ValueError(f"Only StreamFacade is supported by ConcurrentSource. Got {stream}")
        return streams_as_abstract_streams
