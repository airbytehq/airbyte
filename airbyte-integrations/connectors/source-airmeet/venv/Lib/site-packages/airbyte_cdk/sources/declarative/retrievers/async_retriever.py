# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.async_job.job import AsyncJob
from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector
from airbyte_cdk.sources.declarative.partition_routers.async_job_partition_router import (
    AsyncJobPartitionRouter,
)
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState
from airbyte_cdk.sources.utils.slice_logger import AlwaysLogSliceLogger


@dataclass
class AsyncRetriever(Retriever):
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    record_selector: RecordSelector
    stream_slicer: AsyncJobPartitionRouter
    slice_logger: AlwaysLogSliceLogger = field(
        init=False,
        default_factory=lambda: AlwaysLogSliceLogger(),
    )

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    @property
    def exit_on_rate_limit(self) -> bool:
        """
        Whether to exit on rate limit. This is a property of the job repository
        and not the stream slicer. The stream slicer is responsible for creating
        the jobs, but the job repository is responsible for managing the rate
        limits and other job-related properties.

        Note:
         - If the `creation_requester` cannot place / create the job - it might be the case of the RateLimits
         - If the `creation_requester` can place / create the job - it means all other requesters should successfully manage
           to complete the results.
        """
        job_orchestrator = self.stream_slicer._job_orchestrator
        if job_orchestrator is None:
            # Default value when orchestrator is not available
            return False
        return job_orchestrator._job_repository.creation_requester.exit_on_rate_limit  # type: ignore

    @exit_on_rate_limit.setter
    def exit_on_rate_limit(self, value: bool) -> None:
        """
        Sets the `exit_on_rate_limit` property of the job repository > creation_requester,
        meaning that the Job cannot be placed / created if the rate limit is reached.
        Thus no further work on managing jobs is expected to be done.
        """
        job_orchestrator = self.stream_slicer._job_orchestrator
        if job_orchestrator is not None:
            job_orchestrator._job_repository.creation_requester.exit_on_rate_limit = value  # type: ignore[attr-defined, assignment]

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

    def _get_stream_state(self) -> StreamState:
        """
        Gets the current state of the stream.

        Returns:
            StreamState: Mapping[str, Any]
        """

        return self.state

    def _validate_and_get_stream_slice_jobs(
        self, stream_slice: Optional[StreamSlice] = None
    ) -> Iterable[AsyncJob]:
        """
        Validates the stream_slice argument and returns the partition from it.

        Args:
            stream_slice (Optional[StreamSlice]): The stream slice to validate and extract the partition from.

        Returns:
            AsyncPartition: The partition extracted from the stream_slice.

        Raises:
            AirbyteTracedException: If the stream_slice is not an instance of StreamSlice or if the partition is not present in the stream_slice.

        """
        return stream_slice.extra_fields.get("jobs", []) if stream_slice else []

    def stream_slices(self) -> Iterable[Optional[StreamSlice]]:
        yield from self.stream_slicer.stream_slices()

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        # emit the slice_descriptor log message, for connector builder TestRead
        yield self.slice_logger.create_slice_log_message(stream_slice.cursor_slice)  # type: ignore

        stream_state: StreamState = self._get_stream_state()
        jobs: Iterable[AsyncJob] = self._validate_and_get_stream_slice_jobs(stream_slice)
        records: Iterable[Mapping[str, Any]] = self.stream_slicer.fetch_records(jobs)

        yield from self.record_selector.filter_and_transform(
            all_data=records,
            stream_state=stream_state,
            records_schema=records_schema,
            stream_slice=stream_slice,
        )
