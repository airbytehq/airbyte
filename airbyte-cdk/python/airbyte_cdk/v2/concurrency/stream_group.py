import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Mapping, Any, Generic, TypeVar, Iterable, AsyncIterable

from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message

from airbyte_cdk.sources.connector_state_manager import HashableStreamDescriptor
from airbyte_protocol.models import ConfiguredAirbyteCatalog, AirbyteMessage, Type as MessageType, AirbyteStateMessage, AirbyteStateType, \
    AirbyteStreamState, StreamDescriptor

from airbyte_cdk.v2 import Stream
from airbyte_cdk.v2.concurrency import PartitionedStream, PartitionDescriptor, ConcurrencyPolicy, AsyncRequester
from airbyte_cdk.v2.concurrency.concurrent_utils import consume_async_iterable
from airbyte_cdk.v2.state_obj import State

PartitionType = TypeVar('PartitionType', bound=PartitionDescriptor)
StateType = TypeVar('StateType', bound=State)


@dataclass
class StreamAndPartition(Generic[PartitionType]):
    stream: PartitionedStream
    partition_descriptor: PartitionType


class ConcurrentStreamGroup(ABC, Generic[PartitionType]):
    requester: AsyncRequester
    concurrency_policy: ConcurrencyPolicy
    _streams: List[PartitionedStream]

    def __init__(self, requester: AsyncRequester, concurrency_policy: ConcurrencyPolicy, streams: List[PartitionedStream]):
        self.requester = requester
        self.concurrency_policy = concurrency_policy
        self._streams = streams  # TODO we probably don't need full streams, as long as we can get partitions and stream names

    def streams(self, configured_catalog: ConfiguredAirbyteCatalog) -> List[PartitionedStream]:
        # TODO
        return self._streams

    async def _read_partition(self, partition_and_stream: StreamAndPartition[PartitionType]) -> AsyncIterable[AirbyteMessage]:
        partition_descriptor = partition_and_stream.partition_descriptor
        stream = partition_and_stream.stream
        stream_state_manager = stream.state_manager
        # TODO parsing and error handling
        # TODO this likely needs to be an async for because request() should probably return an async iterable
        async for response in self.requester.request(partition_descriptor):
            async for record_or_message in stream.parse_response(response):
                if isinstance(record_or_message, dict):
                    message = stream_data_to_airbyte_message(stream.name, record_or_message)
                yield message

                if message.type == MessageType.RECORD:
                    if state_message := stream_state_manager.observe(message.record.data):
                        yield self._to_state_message(state_message, stream)

        yield self._to_state_message(stream_state_manager.notify_partition_complete(partition_descriptor), stream)

    @staticmethod
    def _to_state_message(state_message, stream):
        return AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name=stream.name, namespace=stream.namespace),
                stream_state=state_message.to_dict()
            ))

    import asyncio

    async def _read_partitions_async(self, partitions_with_streams: Iterable[StreamAndPartition[PartitionType]]):
        semaphore = asyncio.Semaphore(self.concurrency_policy.maximum_number_of_concurrent_requests())
        queue = asyncio.Queue()

        async def process_partition_and_stream(partition_and_stream):
            async with semaphore:
                # print(f'acquired semaphore: {semaphore._value}')
                try:
                    async for x in self._read_partition(partition_and_stream):
                        await queue.put(x)  # Instead of yielding, put the result in the queue
                except Exception as e:
                    await queue.put(e)  # If there was an error, put the error in the queue
                finally:
                    await queue.put(None)  # Sentinel value to indicate this generator is done

        # create a separate task for each partition_and_stream
        tasks = [asyncio.create_task(process_partition_and_stream(partition_and_stream)) for partition_and_stream in
                 partitions_with_streams]

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

    def read_all(self,
                 config: Mapping[str, Any],
                 catalog: ConfiguredAirbyteCatalog,
                 source_state: Mapping[HashableStreamDescriptor, State]
                 ) -> Iterable[AirbyteMessage]:
        partition_descriptors = self.get_partition_descriptors(catalog=catalog, source_state=source_state)
        yield from consume_async_iterable(self._read_partitions_async(partition_descriptors))

    def get_partition_descriptors(self,
                                  catalog: ConfiguredAirbyteCatalog,
                                  source_state: Mapping[HashableStreamDescriptor, State]
                                  ) -> Iterable[StreamAndPartition[PartitionType]]:
        # TODO allow getting the last partition from each stream's partitions so we can enable fast first-syncs
        # TODO allow round-robin getting one stream from each partition to enable "balanced" syncs
        for stream in self._streams:
            stream_state = None  # source_state.get(stream.get_stream_descriptor(), {})
            for partition in stream.get_partition_descriptors(stream_state=stream_state, catalog=catalog):
                yield StreamAndPartition(stream=stream, partition_descriptor=partition)
