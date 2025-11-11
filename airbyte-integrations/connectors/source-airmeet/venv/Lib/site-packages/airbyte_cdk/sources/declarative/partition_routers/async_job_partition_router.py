# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import InitVar, dataclass, field
from typing import Any, Callable, Iterable, Mapping, Optional

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob
from airbyte_cdk.sources.declarative.async_job.job_orchestrator import (
    AsyncJobOrchestrator,
)
from airbyte_cdk.sources.declarative.partition_routers.single_partition_router import (
    SinglePartitionRouter,
)
from airbyte_cdk.sources.streams.concurrent.partitions.stream_slicer import StreamSlicer
from airbyte_cdk.sources.types import Config, StreamSlice
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


@dataclass
class AsyncJobPartitionRouter(StreamSlicer):
    """
    Partition router that creates async jobs in a source API, periodically polls for job
    completion, and supplies the completed job URL locations as stream slices so that
    records can be extracted.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    job_orchestrator_factory: Callable[[Iterable[StreamSlice]], AsyncJobOrchestrator]
    stream_slicer: StreamSlicer = field(
        default_factory=lambda: SinglePartitionRouter(parameters={})
    )

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._job_orchestrator_factory = self.job_orchestrator_factory
        self._job_orchestrator: Optional[AsyncJobOrchestrator] = None
        self._parameters = parameters

    def stream_slices(self) -> Iterable[StreamSlice]:
        slices = self.stream_slicer.stream_slices()
        self._job_orchestrator = self._job_orchestrator_factory(slices)

        for completed_partition in self._job_orchestrator.create_and_get_completed_partitions():
            yield StreamSlice(
                partition=dict(completed_partition.stream_slice.partition),
                cursor_slice=completed_partition.stream_slice.cursor_slice,
                extra_fields={"jobs": list(completed_partition.jobs)},
            )

    def fetch_records(self, async_jobs: Iterable[AsyncJob]) -> Iterable[Mapping[str, Any]]:
        """
        This method of fetching records extends beyond what a PartitionRouter/StreamSlicer should
        be responsible for. However, this was added in because the JobOrchestrator is required to
        retrieve records. And without defining fetch_records() on this class, we're stuck with either
        passing the JobOrchestrator to the AsyncRetriever or storing it on multiple classes.
        """

        if not self._job_orchestrator:
            raise AirbyteTracedException(
                message="Invalid state within AsyncJobRetriever. Please contact Airbyte Support",
                internal_message="AsyncPartitionRepository is expected to be accessed only after `stream_slices`",
                failure_type=FailureType.system_error,
            )

        return self._job_orchestrator.fetch_records(async_jobs=async_jobs)
