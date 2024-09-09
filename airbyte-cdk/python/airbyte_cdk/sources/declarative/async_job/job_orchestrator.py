# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
import time
from typing import Any, Generator, Iterable, List, Mapping, Optional, Set

from airbyte_cdk import StreamSlice
from airbyte_cdk.logger import lazy_log
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob
from airbyte_cdk.sources.declarative.async_job.repository import AsyncJobRepository
from airbyte_cdk.sources.declarative.async_job.status import AsyncJobStatus
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

LOGGER = logging.getLogger("airbyte")


class AsyncPartition:
    """
    This bucket of api_jobs is a bit useless for this iteration but should become interesting when we will be able to split jobs
    """

    _MAX_NUMBER_OF_ATTEMPTS = 3

    def __init__(self, jobs: List[AsyncJob], stream_slice: StreamSlice) -> None:
        self._attempts_per_job = {job: 0 for job in jobs}
        self._stream_slice = stream_slice

    def has_reached_max_attempt(self) -> bool:
        return any(map(lambda attempt_count: attempt_count >= self._MAX_NUMBER_OF_ATTEMPTS, self._attempts_per_job.values()))

    def replace_job(self, job_to_replace: AsyncJob, new_jobs: List[AsyncJob]) -> None:
        current_attempt_count = self._attempts_per_job.pop(job_to_replace, None)
        if current_attempt_count is None:
            raise ValueError("Could not find job to replace")
        elif current_attempt_count >= self._MAX_NUMBER_OF_ATTEMPTS:
            raise ValueError(f"Max attempt reached for job in partition {self._stream_slice}")

        new_attempt_count = current_attempt_count + 1
        for job in new_jobs:
            self._attempts_per_job[job] = new_attempt_count

    def should_split(self, job: AsyncJob) -> bool:
        """
        Not used right now but once we support job split, we should split based on the number of attempts
        """
        return False

    @property
    def jobs(self) -> Iterable[AsyncJob]:
        return self._attempts_per_job.keys()

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

    def __repr__(self) -> str:
        return f"AsyncPartition(stream_slice={self._stream_slice}, attempt_per_job={self._attempts_per_job})"


class AsyncJobOrchestrator:
    _WAIT_TIME_BETWEEN_STATUS_UPDATE_IN_SECONDS = 5

    def __init__(
        self,
        job_repository: AsyncJobRepository,
        slices: Iterable[StreamSlice],
        number_of_retries: Optional[int] = None,
    ) -> None:
        self._job_repository: AsyncJobRepository = job_repository
        self._slice_iterator = iter(slices)
        self._running_partitions: List[AsyncPartition] = []

    def _replace_failed_jobs(self, partition: AsyncPartition) -> None:
        failed_status_jobs = (AsyncJobStatus.FAILED, AsyncJobStatus.TIMED_OUT)
        jobs_to_replace = [job for job in partition.jobs if job.status() in failed_status_jobs]
        for job in jobs_to_replace:
            new_job = self._job_repository.start(job.job_parameters())
            partition.replace_job(job, [new_job])

    def _start_jobs(self) -> None:
        """
        Retry failed jobs and start jobs for each slice in the slice iterator.
        This method iterates over the running jobs and slice iterator and starts a job for each slice.
        The started jobs are added to the running partitions.
        Returns:
            None

        TODO Eventually, we need to cap the number of concurrent jobs.
        However, the first iteration is for sendgrid which only has one job.
        """
        for partition in self._running_partitions:
            self._replace_failed_jobs(partition)

        for _slice in self._slice_iterator:
            job = self._job_repository.start(_slice)
            self._running_partitions.append(AsyncPartition([job], _slice))

    def _get_running_jobs(self) -> Set[AsyncJob]:
        """
        Returns a set of running AsyncJob objects.

        Returns:
            Set[AsyncJob]: A set of AsyncJob objects that are currently running.
        """
        return {job for partition in self._running_partitions for job in partition.jobs if job.status() == AsyncJobStatus.RUNNING}

    def _update_jobs_status(self) -> None:
        """
        Update the status of all running jobs in the repository.
        """
        running_jobs = self._get_running_jobs()
        if running_jobs:
            # update the status only if there are RUNNING jobs
            self._job_repository.update_jobs_status(running_jobs)

    def _wait_on_status_update(self) -> None:
        """
        Waits for a specified amount of time between status updates.


        This method is used to introduce a delay between status updates in order to avoid excessive polling.
        The duration of the delay is determined by the value of `_WAIT_TIME_BETWEEN_STATUS_UPDATE_IN_SECONDS`.

        Returns:
            None
        """
        lazy_log(
            LOGGER,
            logging.DEBUG,
            lambda: f"Polling status in progress. There are currently {len(self._running_partitions)} running partitions.",
        )

        # wait only when there are running partitions
        if self._running_partitions:
            lazy_log(
                LOGGER,
                logging.DEBUG,
                lambda: f"Waiting for {self._WAIT_TIME_BETWEEN_STATUS_UPDATE_IN_SECONDS} seconds before next poll...",
            )
            time.sleep(self._WAIT_TIME_BETWEEN_STATUS_UPDATE_IN_SECONDS)

    def _process_completed_partition(self, partition: AsyncPartition) -> None:
        """
        Process a completed partition.
        Args:
            partition (AsyncPartition): The completed partition to process.
        """
        job_ids = list(map(lambda job: job.api_job_id(), {job for job in partition.jobs}))
        LOGGER.info(f"The following jobs for stream slice {partition.stream_slice} have been completed: {job_ids}.")

    def _process_running_partitions_and_yield_completed_ones(self) -> Generator[AsyncPartition, Any, None]:
        """
        Process the running partitions.

        Yields:
            AsyncPartition: The processed partition.

        Raises:
            Any: Any exception raised during processing.
        """
        current_running_partitions: List[AsyncPartition] = []
        for partition in self._running_partitions:
            match partition.status:
                case AsyncJobStatus.COMPLETED:
                    self._process_completed_partition(partition)
                    yield partition
                case AsyncJobStatus.RUNNING:
                    current_running_partitions.append(partition)
                case _ if partition.has_reached_max_attempt():
                    self._process_partitions_with_errors(partition)
                case _:
                    # job will be restarted in `_start_job`
                    current_running_partitions.insert(0, partition)
        # update the referenced list with running partitions
        self._running_partitions = current_running_partitions

    def _process_partitions_with_errors(self, partition: AsyncPartition) -> None:
        """
        Process a partition with status errors (FAILED and TIMEOUT).

        Args:
            partition (AsyncPartition): The partition to process.
        Returns:
            AirbyteTracedException: An exception indicating that at least one job could not be completed.
        Raises:
            AirbyteTracedException: If at least one job could not be completed.
        """
        status_by_job_id = {job.api_job_id(): job.status() for job in partition.jobs}
        raise AirbyteTracedException(
            message=f"At least one job could not be completed. Job statuses were: {status_by_job_id}",
            failure_type=FailureType.system_error,
        )

    def create_and_get_completed_partitions(self) -> Iterable[AsyncPartition]:
        """
        Creates and retrieves completed partitions.
        This method continuously starts jobs, updates job status, processes running partitions,
        logs polling partitions, and waits for status updates. It yields completed partitions
        as they become available.

        Returns:
            An iterable of completed partitions, represented as AsyncPartition objects.
            Each partition is wrapped in an Optional, allowing for None values.
        """
        while True:
            self._start_jobs()
            if not self._running_partitions:
                break

            self._update_jobs_status()
            yield from self._process_running_partitions_and_yield_completed_ones()
            self._wait_on_status_update()

    def fetch_records(self, partition: AsyncPartition) -> Iterable[Mapping[str, Any]]:
        """
        Fetches records from the given partition's jobs.

        Args:
            partition (AsyncPartition): The partition containing the jobs.

        Yields:
            Iterable[Mapping[str, Any]]: The fetched records from the jobs.
        """
        for job in partition.jobs:
            yield from self._job_repository.fetch_records(job)
