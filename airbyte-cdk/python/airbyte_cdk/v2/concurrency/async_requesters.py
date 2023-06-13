from abc import abstractmethod, ABC
from collections.abc import AsyncIterable
from typing import Generic, TypeVar, AsyncIterator

PartitionType = TypeVar('PartitionType', bound='PartitionDescriptor')
ResponseType = TypeVar('ResponseType')


class AsyncRequester(ABC, Generic[PartitionType]):
    @abstractmethod
    # TODO this likely needs to be an async iterable
    async def request(self, partition_descriptor: PartitionType) -> AsyncIterable[ResponseType]:
        """
        Retrieves the data associated with the input partition descriptor.
        The return value should be an async generator which contains one or more responses
        """
        # TODO this should be able to handle differing pagination/error handling/etc.. strategies between partitions
