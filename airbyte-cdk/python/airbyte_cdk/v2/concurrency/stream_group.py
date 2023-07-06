#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
from abc import ABC
from dataclasses import dataclass
from typing import Any, AsyncIterable, Generic, Iterable, List, Mapping, TypeVar

from airbyte_cdk.sources.connector_state_manager import HashableStreamDescriptor
from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.v2.concurrency.async_requesters import Client
from airbyte_cdk.v2.concurrency.concurrency_policy import ConcurrencyPolicy
from airbyte_cdk.v2.concurrency.concurrent_utils import consume_async_iterable
from airbyte_cdk.v2.concurrency.http import HttpRequestDescriptor
from airbyte_cdk.v2.concurrency.partition_descriptors import PartitionDescriptor
from airbyte_cdk.v2.state_obj import State
from airbyte_protocol.models import (
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    StreamDescriptor,
)
from airbyte_protocol.models import Type as MessageType
import requests

PartitionType = TypeVar("PartitionType", bound=PartitionDescriptor)
RequestType = TypeVar("RequestType")
StateType = TypeVar("StateType", bound=State)


@dataclass
class StreamAndPartition(Generic[PartitionType]):
    stream: Stream
    partition_descriptor: PartitionType

@dataclass
class StreamAndPartitionAndRequest(Generic[PartitionType, RequestType]):
    stream: Stream
    partition_descriptor: PartitionType
    request: RequestType


class ConcurrentStreamGroup(ABC, Generic[PartitionType]):
    _requester_client: Client
    _concurrency_policy: ConcurrencyPolicy
    _streams: List[Stream]

    def __init__(self, requester_client, concurrency_policy: ConcurrencyPolicy, streams: List[Stream]):
        self.requester_client = requester_client
        self._streams = streams  # TODO we probably don't need full streams, as long as we can get partitions and stream names
        self._concurrency_policy = concurrency_policy

    def streams(self, configured_catalog: ConfiguredAirbyteCatalog) -> List[Stream]:
        # TODO
        return self._streams

    async def _read_partition(self, partition_and_stream_and_request: StreamAndPartitionAndRequest[PartitionType, HttpRequestDescriptor]) -> AsyncIterable[requests.Response]:
        stream = partition_and_stream_and_request.stream
        request = partition_and_stream_and_request.request
        yield await self.requester_client.request(request)

    @staticmethod
    def _to_state_message(state_message, stream):
        return AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name=stream.name, namespace=stream.namespace), stream_state=state_message.to_dict()
            ),
        )

    async def _read_partitions_async(self, partitions_with_streams: Iterable[StreamAndPartition[PartitionType]]):
        semaphore = asyncio.Semaphore(self._concurrency_policy.maximum_number_of_concurrent_requests() + 1000)
        queue = asyncio.Queue()
        task_queue = asyncio.Queue()

        async def process_partition_and_stream(partition_and_stream):
            async with semaphore:
                try:
                    async for x in self._read_partition(partition_and_stream):
                        await queue.put(x)  # Instead of yielding, put the result in the queue
                except Exception as e:
                    await queue.put(e)  # If there was an error, put the error in the queue
                finally:
                    await queue.put(None)  # Sentinel value to indicate this generator is done

        async def pull_from_queue():
            async with semaphore:
                try:
                    print(f"pull_from_queue")
                    work_item = await task_queue.get()
                    print(f"work_item: {work_item}")
                except Exception as e:
                    await queue.put(e)
                finally:
                    await queue.put(None)

        for partition_and_stream in partitions_with_streams:
            partition = partition_and_stream.partition_descriptor
            stream = partition_and_stream.stream
            request = stream.get_request_generator().next_request(partition, None)
            await task_queue.put(StreamAndPartitionAndRequest(stream=stream, partition_descriptor=partition, request=request))


        # create a separate task for each partition_and_stream
        tasks = [
            #asyncio.create_task(process_partition_and_stream(partition_and_stream)) for partition_and_stream in partitions_with_streams
            asyncio.create_task(pull_from_queue()) for partition_and_stream in partitions_with_streams
        ]

        num_active_generators = len(tasks)
        while not task_queue.empty():
            x = await queue.get()
            if x is None:  # If we get the sentinel value, decrement the count of active generators
                num_active_generators -= 1
            elif isinstance(x, Exception):  # If we get an exception, raise it
                # Cancel all other tasks and raise the exception
                for task in tasks:
                    task.cancel()
                raise x
            else:  # Otherwise, yield the value
                yield x

        # Wait for all tasks to complete (they should already be done at this point)
        await asyncio.gather(*tasks)

    def read_all(
        self, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, source_state: Mapping[HashableStreamDescriptor, State]
    ) -> Iterable[AirbyteMessage]:
        partition_descriptors = self.get_partition_descriptors(catalog=catalog, source_state=source_state)
        yield from consume_async_iterable(self._read_partitions_async(partition_descriptors))

    def get_partition_descriptors(
        self, catalog: ConfiguredAirbyteCatalog, source_state: Mapping[HashableStreamDescriptor, State]
    ) -> Iterable[StreamAndPartitionAndRequest[PartitionType, HttpRequestDescriptor]]:
        # TODO allow getting the last partition from each stream's partitions so we can enable fast first-syncs
        # TODO allow round-robin getting one stream from each partition to enable "balanced" syncs
        for stream in self._streams:
            stream_state = None  # source_state.get(stream.get_stream_descriptor(), {})
            for partition in stream.generate_partitions(stream_state=stream_state):
                request = stream.get_request_generator().next_request(partition, None)
                yield StreamAndPartitionAndRequest(stream=stream, partition_descriptor=partition, request=request)
