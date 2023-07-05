from abc import abstractmethod, ABC
from collections.abc import AsyncIterable
from typing import Generic, TypeVar, AsyncIterator

from airbyte_cdk.v2.concurrency.partition_descriptors import PartitionDescriptor

ClientType = TypeVar('ClientType', bound='RequesterType')
ResponseType = TypeVar('ResponseType')
RequestType = TypeVar('RequestType')


class Client(ABC, Generic[RequestType, ResponseType]):
    @abstractmethod
    async def request(self, request: RequestType) -> ResponseType:
        pass


class AsyncRequester(ABC):
    @abstractmethod
    # TODO this likely needs to be an async iterable
    async def request(self, partition_descriptor: PartitionDescriptor) -> AsyncIterable[ResponseType]:
        """
        Retrieves the data associated with the input partition descriptor.
        The return value should be an async generator which contains one or more responses
        """
        # TODO this should be able to handle differing pagination/error handling/etc.. strategies between partitions


class DefaultAsyncRequester(AsyncRequester):
    async def request(self, partition_descriptor: PartitionDescriptor) -> AsyncIterable[ResponseType]:
        yield None
