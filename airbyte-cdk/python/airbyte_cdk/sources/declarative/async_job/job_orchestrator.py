# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import logging
import time
from typing import Any, Iterable, List, Mapping, Set

from airbyte_cdk import StreamSlice
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob, AsyncJobStatus
from airbyte_cdk.sources.declarative.async_job.repository import AsyncJobRepository
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_protocol.models import FailureType


class AsyncPartition:
    """
    This bucket of api_jobs is a bit useless for this iteration but should become interesting when we will be able to split jobs
    """

    def __init__(self, jobs: List[AsyncJob], stream_slice: StreamSlice) -> None:
        self._jobs = jobs
        self._stream_slice = stream_slice

    @property
    def jobs(self) -> List[AsyncJob]:
        return self._jobs

    @property
    def stream_slice(self) -> StreamSlice:
        return self._stream_slice

    @property
    def status(self) -> AsyncJobStatus:
        """
        Given different job statuses, the priority is: FAILED, TIMED_OUT, RUNNING. Else, it means everything is completed.
        """
        statuses = set(map(lambda job: job.status(), self.jobs))
        if statuses == {AsyncJobStatus.COMPLETED}:
            return AsyncJobStatus.COMPLETED
        elif AsyncJobStatus.FAILED in statuses:
            return AsyncJobStatus.FAILED
        elif AsyncJobStatus.TIMED_OUT in statuses:
            return AsyncJobStatus.TIMED_OUT
        else:
            return AsyncJobStatus.RUNNING

    # TODO def __repr__(self) -> str: for slice printing


class AsyncJobOrchestrator:
    _WAIT_TIME_BETWEEN_STATUS_UPDATE_IN_SECONDS = 5

    def __init__(self, job_repository: AsyncJobRepository, slices: Iterable[StreamSlice]):
        self._job_repository: AsyncJobRepository = job_repository
        self._slice_iterator = iter(slices)
        self._logger = logging.getLogger("airbyte")

        self._running_partitions: List[AsyncPartition] = []

    def create_and_get_completed_partitions(self) -> Iterable[AsyncPartition]:
        while True:
            self._start_jobs()
            if not self._running_partitions:
                break

            self._job_repository.update_jobs_status(self._get_running_jobs())

            current_running_partitions: List[AsyncPartition] = []
            for partition in self._running_partitions:
                if partition.status == AsyncJobStatus.COMPLETED:
                    job_ids = list(map(lambda job: job.api_job_id(), {job for job in partition.jobs}))
                    self._logger.info(f"The following jobs for stream slice {partition.stream_slice} have been completed: {job_ids}.")
                    yield partition
                elif partition.status == AsyncJobStatus.RUNNING:
                    current_running_partitions.append(partition)
                else:
                    status_by_job_id = {job.api_job_id(): job.status() for job in partition.jobs}
                    raise AirbyteTracedException(
                        message=f"At least one job could not be completed. Job statuses were: {status_by_job_id}",
                        failure_type=FailureType.system_error,
                    )

            self._running_partitions = current_running_partitions

            if self._logger.isEnabledFor(logging.DEBUG):
                # if statement in order to avoid string formatting if we're not in debug mode
                self._logger.debug(
                    f"Polling status completed. There are currently {len(self._running_partitions)} running partitions. Waiting for {self._WAIT_TIME_BETWEEN_STATUS_UPDATE_IN_SECONDS} seconds before next poll..."
                )
            time.sleep(self._WAIT_TIME_BETWEEN_STATUS_UPDATE_IN_SECONDS)

    def _start_jobs(self) -> None:
        """
        TODO Eventually, we need to cap the number of concurrent jobs.
        However, the first iteration is for sendgrid which only has one job.
        """
        for _slice in self._slice_iterator:
            job = self._job_repository.start(_slice)
            self._running_partitions.append(AsyncPartition([job], _slice))

    def _get_running_jobs(self) -> Set[AsyncJob]:
        return {job for partition in self._running_partitions for job in partition.jobs if job.status() == AsyncJobStatus.RUNNING}

    def fetch_records(self, partition: AsyncPartition) -> Iterable[Mapping[str, Any]]:
        for job in partition.jobs:
            yield from self._job_repository.fetch_records(job)
