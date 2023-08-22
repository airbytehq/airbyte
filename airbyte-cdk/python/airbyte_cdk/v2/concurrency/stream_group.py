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

PartitionType = TypeVar("PartitionType", bound=PartitionDescriptor)
StateType = TypeVar("StateType", bound=State)


@dataclass
class StreamAndPartition(Generic[PartitionType]):
    stream: Stream
    partition_descriptor: PartitionType


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

    async def read_partition(self, partition_and_stream: StreamAndPartition[PartitionType]) -> AsyncIterable[AirbyteMessage]:
        partition_descriptor = partition_and_stream.partition_descriptor
        stream = partition_and_stream.stream
        #stream_state_manager = stream.state_manager_class()
        # TODO parsing and error handling
        # TODO this likely needs to be an async for because request() should probably return an async iterable
        # print(f"partition_descriptor: {partition_descriptor}")
        pagination_complete = False
        last_response = None
        request_generator = stream.get_request_generator()
        while True:
            # It's not obvious from the interface, but this technically needs the records that are produced from the last response
            # This dependency is made explicit in the declarative framework
            request = await request_generator.next_request(partition_descriptor, last_response)
            if not request:
                break

            response = await self.requester_client.request(request)
            last_response = response
            # async for response in self.requester.request(partition_descriptor):
            # print(f"response: {response}")
            # print(f"stream.parse_response(response): {stream.parse_response(response)}")
            # FFIXME: should parsing be async?
            # I think it would be better, but it makes the integration more complicated
            for record_or_message in stream.parse_response(response, stream_state={}):
                if isinstance(record_or_message, dict):
                    message = stream_data_to_airbyte_message(stream.name, record_or_message)
                elif isinstance(record_or_message, Record):
                    message = stream_data_to_airbyte_message(stream.name, record_or_message.data)
                else:
                    raise ValueError(f"Unexpected type: {type(record_or_message)}")
                yield message

                # FIXME: This feels off. The requester should only produce record messages
                # If there are other message types to be produced, they should be passed using the message repository
                #if message.type == MessageType.RECORD:
                    #if state_message := stream_state_manager.observe(message.record.data):
                    #    pass
                        # In what scenario do we need up update the state mid-partition?
                        # imo this adds complexity
                        # yield self._to_state_message(state_message, stream)

        #yield self._to_state_message(stream_state_manager.notify_partition_complete(partition_descriptor), stream)

    @staticmethod
    def _to_state_message(state_message, stream):
        return AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name=stream.name, namespace=stream.namespace), stream_state=state_message.to_dict()
            ),
        )

    async def _read_partitions_async(self, partitions_with_streams: Iterable[StreamAndPartition[PartitionType]]):
        semaphore = asyncio.Semaphore(self._concurrency_policy.maximum_number_of_concurrent_requests())
        queue = asyncio.Queue()

        async def process_partition_and_stream(partition_and_stream):
            async with semaphore:
                # print(f'acquired semaphore: {semaphore._value}')
                try:
                    async for x in self.read_partition(partition_and_stream):
                        await queue.put(x)  # Instead of yielding, put the result in the queue
                except Exception as e:
                    await queue.put(e)  # If there was an error, put the error in the queue
                finally:
                    await queue.put(None)  # Sentinel value to indicate this generator is done

        # create a separate task for each partition_and_stream
        tasks = [
            asyncio.create_task(process_partition_and_stream(partition_and_stream)) for partition_and_stream in partitions_with_streams
        ]

        num_active_generators = len(tasks)
        while num_active_generators > 0:
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
        #partition_descriptors = list(self.get_partition_descriptors(catalog=catalog, source_state=source_state))
        loop = asyncio.get_event_loop()
        partition_descriptors = list(consume_async_iterable(self.get_partition_descriptors(catalog=catalog, source_state=source_state)))
        print(f"partition_descriptors: {partition_descriptors}")
        exit()
        yield from consume_async_iterable(self._read_partitions_async(partition_descriptors))

    async def get_partition_descriptors(
        self, catalog: ConfiguredAirbyteCatalog, source_state: Mapping[HashableStreamDescriptor, State]
    ) -> AsyncIterable[StreamAndPartition[PartitionType]]:
        # TODO allow getting the last partition from each stream's partitions so we can enable fast first-syncs
        # TODO allow round-robin getting one stream from each partition to enable "balanced" syncs
        print(f"all streams: {self._streams}")
        for stream in self._streams:
            stream_state = None  # source_state.get(stream.get_stream_descriptor(), {})
            print(f"getting partitions for {stream}")
            partitions = await stream.generate_partitions(stream_state=stream_state, concurrency_stream_group=self)
            for partition in partitions:
            #for partition in consume_async_iterable(stream.generate_partitions(stream_state=stream_state, concurrency_stream_group=self)):
                yield StreamAndPartition(stream=stream, partition_descriptor=partition)
