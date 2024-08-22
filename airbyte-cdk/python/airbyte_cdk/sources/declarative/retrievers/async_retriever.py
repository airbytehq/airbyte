# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Iterable, Mapping, Optional, Callable

from airbyte_protocol.models import FailureType

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.sources.declarative.retrievers import Retriever
from airbyte_cdk.sources.declarative.stream_slicers import StreamSlicer
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.job.partition_repository import JobOrchestrator
from airbyte_cdk.sources.streams.core import StreamData


class AsyncRetriever(Retriever):
    def __init__(self, stream_slicer: StreamSlicer, async_partition_repository_factory: Callable[[Iterable[StreamSlice]], JobOrchestrator]) -> None:
        self._stream_slicer = stream_slicer
        self._async_partition_repository_factory = async_partition_repository_factory
        self.__async_partition_repository: Optional[JobOrchestrator] = None


    def stream_slices(self) -> Iterable[Optional[StreamSlice]]:
        self.__async_partition_repository = self._async_partition_repository_factory(self._stream_slicer.stream_slices())

        for completed_partition in self._async_partition_repository.get_completed_partitions():
            yield {"partition": completed_partition}

    def read_records(self, records_schema: Mapping[str, Any], stream_slice: Optional[StreamSlice] = None) -> Iterable[StreamData]:
        if not stream_slice or "partition" not in stream_slice:
            raise AirbyteTracedException(
                message="Invalid arguments to AsyncJobRetriever.read_records: stream_slice is no optional. Please contact Airbyte Support",
                failure_type=FailureType.system_error,
            )
        yield from self._async_partition_repository.fetch_records(stream_slice["partition"])

    @property
    def state(self) -> StreamState:
        """
        As a first iteration for sendgrid, there is no state to be managed
        """
        return {}

    @state.setter
    def state(self, value: StreamState) -> None:
        """
        As a first iteration for sendgrid, there is no state to be managed
        """
        pass

    @property
    def _async_partition_repository(self) -> JobOrchestrator:
        if self.__async_partition_repository:
            return self.__async_partition_repository

        raise AirbyteTracedException(
            message="Invalid state within AsyncJobRetriever. Please contact Airbyte Support",
            internal_message="AsyncPartitionRepository is expected to be accessed only after `stream_slices`",
            failure_type=FailureType.system_error,
        )
