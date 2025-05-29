# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from dataclasses import InitVar, dataclass, field
from typing import Any, Callable, Iterable, Mapping, Optional

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.async_job.job_orchestrator import AsyncJobOrchestrator, AsyncPartition
from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector
from airbyte_cdk.sources.declarative.partition_routers import SinglePartitionRouter
from airbyte_cdk.sources.declarative.retrievers import Retriever
from airbyte_cdk.sources.declarative.stream_slicers import StreamSlicer
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


@dataclass
class AsyncRetriever(Retriever):
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    job_orchestrator_factory: Callable[[Iterable[StreamSlice]], AsyncJobOrchestrator]
    record_selector: RecordSelector
    stream_slicer: StreamSlicer = field(default_factory=lambda: SinglePartitionRouter(parameters={}))

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._job_orchestrator_factory = self.job_orchestrator_factory
        self.__job_orchestrator: Optional[AsyncJobOrchestrator] = None
        self._parameters = parameters

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
    def _job_orchestrator(self) -> AsyncJobOrchestrator:
        if not self.__job_orchestrator:
            raise AirbyteTracedException(
                message="Invalid state within AsyncJobRetriever. Please contact Airbyte Support",
                internal_message="AsyncPartitionRepository is expected to be accessed only after `stream_slices`",
                failure_type=FailureType.system_error,
            )

        return self.__job_orchestrator

    def _get_stream_state(self) -> StreamState:
        """
        Gets the current state of the stream.

        Returns:
            StreamState: Mapping[str, Any]
        """

        return self.state

    def _validate_and_get_stream_slice_partition(self, stream_slice: Optional[StreamSlice] = None) -> AsyncPartition:
        """
        Validates the stream_slice argument and returns the partition from it.

        Args:
            stream_slice (Optional[StreamSlice]): The stream slice to validate and extract the partition from.

        Returns:
            AsyncPartition: The partition extracted from the stream_slice.

        Raises:
            AirbyteTracedException: If the stream_slice is not an instance of StreamSlice or if the partition is not present in the stream_slice.

        """
        if not isinstance(stream_slice, StreamSlice) or "partition" not in stream_slice.partition:
            raise AirbyteTracedException(
                message="Invalid arguments to AsyncJobRetriever.read_records: stream_slice is no optional. Please contact Airbyte Support",
                failure_type=FailureType.system_error,
            )
        return stream_slice["partition"]  # type: ignore  # stream_slice["partition"] has been added as an AsyncPartition as part of stream_slices

    def stream_slices(self) -> Iterable[Optional[StreamSlice]]:
        slices = self.stream_slicer.stream_slices()
        self.__job_orchestrator = self._job_orchestrator_factory(slices)

        for completed_partition in self._job_orchestrator.create_and_get_completed_partitions():
            yield StreamSlice(
                partition=dict(completed_partition.stream_slice.partition) | {"partition": completed_partition},
                cursor_slice=completed_partition.stream_slice.cursor_slice,
            )

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:

        stream_state: StreamState = self._get_stream_state()
        partition: AsyncPartition = self._validate_and_get_stream_slice_partition(stream_slice)
        records: Iterable[Mapping[str, Any]] = self._job_orchestrator.fetch_records(partition)

        yield from self.record_selector.filter_and_transform(
            all_data=records,
            stream_state=stream_state,
            records_schema=records_schema,
            stream_slice=stream_slice,
        )
