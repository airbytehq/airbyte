# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
import threading
import time
import traceback
import uuid
from datetime import timedelta
from typing import (
    Any,
    Generator,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
)

from airbyte_cdk.logger import lazy_log
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob
from airbyte_cdk.sources.declarative.async_job.job_tracker import (
    ConcurrentJobLimitReached,
    JobTracker,
)
from airbyte_cdk.sources.declarative.async_job.repository import AsyncJobRepository
from airbyte_cdk.sources.declarative.async_job.status import AsyncJobStatus
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

LOGGER = logging.getLogger("airbyte")
_NO_TIMEOUT = timedelta.max
_API_SIDE_RUNNING_STATUS = {AsyncJobStatus.RUNNING, AsyncJobStatus.TIMED_OUT}


class AsyncPartition:
    """
    This bucket of api_jobs is a bit useless for this iteration but should become interesting when we will be able to split jobs
    """

    _DEFAULT_MAX_JOB_RETRY = 3

    def __init__(
        self, jobs: List[AsyncJob], stream_slice: StreamSlice, job_max_retry: Optional[int] = None
    ) -> None:
        self._attempts_per_job = {job: 1 for job in jobs}
        self._stream_slice = stream_slice
        self._job_max_retry = (
            job_max_retry if job_max_retry is not None else self._DEFAULT_MAX_JOB_RETRY
        )

    def has_reached_max_attempt(self) -> bool:
        return any(
            map(
                lambda attempt_count: attempt_count >= self._job_max_retry,
                self._attempts_per_job.values(),
            )
        )

    def replace_job(self, job_to_replace: AsyncJob, new_jobs: List[AsyncJob]) -> None:
        current_attempt_count = self._attempts_per_job.pop(job_to_replace, None)
        if current_attempt_count is None:
            raise ValueError("Could not find job to replace")
        elif current_attempt_count >= self._job_max_retry:
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

    def __json_serializable__(self) -> Any:
        return self._stream_slice


T = TypeVar("T")


class LookaheadIterator(Generic[T]):
    def __init__(self, iterable: Iterable[T]) -> None:
        self._iterator = iter(iterable)
        self._buffer: List[T] = []

    def __iter__(self) -> "LookaheadIterator[T]":
        return self

    def __next__(self) -> T:
        if self._buffer:
            return self._buffer.pop()
        else:
            return next(self._iterator)

    def has_next(self) -> bool:
        if self._buffer:
            return True

        try:
            self._buffer = [next(self._iterator)]
        except StopIteration:
            return False
        else:
            return True

    def add_at_the_beginning(self, item: T) -> None:
        self._buffer = [item] + self._buffer


class AsyncJobOrchestrator:
    _WAIT_TIME_BETWEEN_STATUS_UPDATE_IN_SECONDS = 5
    _KNOWN_JOB_STATUSES = {
        AsyncJobStatus.COMPLETED,
        AsyncJobStatus.FAILED,
        AsyncJobStatus.RUNNING,
        AsyncJobStatus.TIMED_OUT,
    }
    _RUNNING_ON_API_SIDE_STATUS = {AsyncJobStatus.RUNNING, AsyncJobStatus.TIMED_OUT}

    def __init__(
        self,
        job_repository: AsyncJobRepository,
        slices: Iterable[StreamSlice],
        job_tracker: JobTracker,
        message_repository: MessageRepository,
        exceptions_to_break_on: Iterable[Type[Exception]] = tuple(),
        has_bulk_parent: bool = False,
        job_max_retry: Optional[int] = None,
    ) -> None:
        """
        If the stream slices provided as a parameters relies on a async job streams that relies on the same JobTracker, `has_bulk_parent`
        needs to be set to True as jobs creation needs to be prioritized on the parent level. Doing otherwise could lead to a situation
        where the child has taken up all the job budget without room to the parent to create more which would lead to an infinite loop of
        "trying to start a parent job" and "ConcurrentJobLimitReached".
        """
        if {*AsyncJobStatus} != self._KNOWN_JOB_STATUSES:
            # this is to prevent developers updating the possible statuses without updating the logic of this class
            raise ValueError(
                "An AsyncJobStatus has been either removed or added which means the logic of this class needs to be reviewed. Once the logic has been updated, please update _KNOWN_JOB_STATUSES"
            )

        self._job_repository: AsyncJobRepository = job_repository
        self._slice_iterator = LookaheadIterator(slices)
        self._running_partitions: List[AsyncPartition] = []
        self._job_tracker = job_tracker
        self._message_repository = message_repository
        self._exceptions_to_break_on: Tuple[Type[Exception], ...] = tuple(exceptions_to_break_on)
        self._has_bulk_parent = has_bulk_parent
        self._job_max_retry = job_max_retry

        self._non_breaking_exceptions: List[Exception] = []

    def _replace_failed_jobs(self, partition: AsyncPartition) -> None:
        failed_status_jobs = (AsyncJobStatus.FAILED, AsyncJobStatus.TIMED_OUT)
        jobs_to_replace = [job for job in partition.jobs if job.status() in failed_status_jobs]
        for job in jobs_to_replace:
            new_job = self._start_job(job.job_parameters(), job.api_job_id())
            partition.replace_job(job, [new_job])

    def _start_jobs(self) -> None:
        """
        Retry failed jobs and start jobs for each slice in the slice iterator.
        This method iterates over the running jobs and slice iterator and starts a job for each slice.
        The started jobs are added to the running partitions.
        Returns:
            None

        However, the first iteration is for sendgrid which only has one job.
        """
        at_least_one_slice_consumed_from_slice_iterator_during_current_iteration = False
        _slice = None
        try:
            for partition in self._running_partitions:
                self._replace_failed_jobs(partition)

            if (
                self._has_bulk_parent
                and self._running_partitions
                and self._slice_iterator.has_next()
            ):
                LOGGER.debug(
                    "This AsyncJobOrchestrator is operating as a child of a bulk stream hence we limit the number of concurrent jobs on the child until there are no more parent slices to avoid the child taking all the API job budget"
                )
                return

            for _slice in self._slice_iterator:
                at_least_one_slice_consumed_from_slice_iterator_during_current_iteration = True
                job = self._start_job(_slice)
                self._running_partitions.append(AsyncPartition([job], _slice, self._job_max_retry))
                if self._has_bulk_parent and self._slice_iterator.has_next():
                    break
        except ConcurrentJobLimitReached:
            if at_least_one_slice_consumed_from_slice_iterator_during_current_iteration:
                # this means a slice has been consumed but the job couldn't be create therefore we need to put it back at the beginning of the _slice_iterator
                self._slice_iterator.add_at_the_beginning(_slice)  # type: ignore  # we know it's not None here because `ConcurrentJobLimitReached` happens during the for loop
            LOGGER.debug(
                "Waiting before creating more jobs as the limit of concurrent jobs has been reached. Will try again later..."
            )

    def _start_job(self, _slice: StreamSlice, previous_job_id: Optional[str] = None) -> AsyncJob:
        if previous_job_id:
            id_to_replace = previous_job_id
            lazy_log(LOGGER, logging.DEBUG, lambda: f"Attempting to replace job {id_to_replace}...")
        else:
            id_to_replace = self._job_tracker.try_to_get_intent()

        try:
            job = self._job_repository.start(_slice)
            self._job_tracker.add_job(id_to_replace, job.api_job_id())
            return job
        except Exception as exception:
            LOGGER.warning(f"Exception has occurred during job creation: {exception}")
            if self._is_breaking_exception(exception):
                self._job_tracker.remove_job(id_to_replace)
                raise exception
            return self._keep_api_budget_with_failed_job(_slice, exception, id_to_replace)

    def _keep_api_budget_with_failed_job(
        self, _slice: StreamSlice, exception: Exception, intent: str
    ) -> AsyncJob:
        """
        We have a mechanism to retry job. It is used when a job status is FAILED or TIMED_OUT. The easiest way to retry is to have this job
        as created in a failed state and leverage the retry for failed/timed out jobs. This way, we don't have to have another process for
        retrying jobs that couldn't be started.
        """
        LOGGER.warning(
            f"Could not start job for slice {_slice}. Job will be flagged as failed and retried if max number of attempts not reached: {exception}"
        )
        traced_exception = (
            exception
            if isinstance(exception, AirbyteTracedException)
            else AirbyteTracedException.from_exception(exception)
        )
        # Even though we're not sure this will break the stream, we will emit here for simplicity's sake. If we wanted to be more accurate,
        # we would keep the exceptions in-memory until we know that we have reached the max attempt.
        self._message_repository.emit_message(traced_exception.as_airbyte_message())
        job = self._create_failed_job(_slice)
        self._job_tracker.add_job(intent, job.api_job_id())
        return job

    def _create_failed_job(self, stream_slice: StreamSlice) -> AsyncJob:
        job = AsyncJob(f"{uuid.uuid4()} - Job that could not start", stream_slice, _NO_TIMEOUT)
        job.update_status(AsyncJobStatus.FAILED)
        return job

    def _get_running_jobs(self) -> Set[AsyncJob]:
        """
        Returns a set of running AsyncJob objects.

        Returns:
            Set[AsyncJob]: A set of AsyncJob objects that are currently running.
        """
        return {
            job
            for partition in self._running_partitions
            for job in partition.jobs
            if job.status() == AsyncJobStatus.RUNNING
        }

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
        LOGGER.info(
            f"The following jobs for stream slice {partition.stream_slice} have been completed: {job_ids}."
        )

        # It is important to remove the jobs from the job tracker before yielding the partition as the caller might try to schedule jobs
        # but won't be able to as all jobs slots are taken even though job is done.
        for job in partition.jobs:
            self._job_tracker.remove_job(job.api_job_id())

    def _process_running_partitions_and_yield_completed_ones(
        self,
    ) -> Generator[AsyncPartition, Any, None]:
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
                    self._stop_partition(partition)
                    self._process_partitions_with_errors(partition)
                case _:
                    self._stop_timed_out_jobs(partition)
                    # re-allocate FAILED jobs, but TIMEOUT jobs are not re-allocated
                    self._reallocate_partition(current_running_partitions, partition)

            # We only remove completed / timeout jobs jobs as we want failed jobs to be re-allocated in priority
            self._remove_completed_jobs(partition)

        # update the referenced list with running partitions
        self._running_partitions = current_running_partitions

    def _stop_partition(self, partition: AsyncPartition) -> None:
        for job in partition.jobs:
            if job.status() in _API_SIDE_RUNNING_STATUS:
                self._abort_job(job, free_job_allocation=True)
            else:
                self._job_tracker.remove_job(job.api_job_id())

    def _stop_timed_out_jobs(self, partition: AsyncPartition) -> None:
        for job in partition.jobs:
            if job.status() == AsyncJobStatus.TIMED_OUT:
                self._abort_job(job, free_job_allocation=False)

    def _abort_job(self, job: AsyncJob, free_job_allocation: bool = True) -> None:
        try:
            self._job_repository.abort(job)
            if free_job_allocation:
                self._job_tracker.remove_job(job.api_job_id())
        except Exception as exception:
            LOGGER.warning(f"Could not free budget for job {job.api_job_id()}: {exception}")

    def _remove_completed_jobs(self, partition: AsyncPartition) -> None:
        """
        Remove completed or timed out jobs from the partition.

        Args:
            partition (AsyncPartition): The partition to process.
        """
        for job in partition.jobs:
            if job.status() == AsyncJobStatus.COMPLETED:
                self._job_tracker.remove_job(job.api_job_id())

    def _reallocate_partition(
        self,
        current_running_partitions: List[AsyncPartition],
        partition: AsyncPartition,
    ) -> None:
        """
        Reallocate the partition by starting a new job for each job in the
        partition.
        Args:
            current_running_partitions (list): The list of currently running partitions.
            partition (AsyncPartition): The partition to reallocate.
        """
        current_running_partitions.insert(0, partition)

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
        self._non_breaking_exceptions.append(
            AirbyteTracedException(
                internal_message=f"At least one job could not be completed for slice {partition.stream_slice}. Job statuses were: {status_by_job_id}. See warning logs for more information.",
                failure_type=FailureType.config_error,
            )
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
            try:
                lazy_log(
                    LOGGER,
                    logging.DEBUG,
                    lambda: f"JobOrchestrator loop - (Thread {threading.get_native_id()}, AsyncJobOrchestrator {self}) is starting the async job loop",
                )
                self._start_jobs()
                if not self._slice_iterator.has_next() and not self._running_partitions:
                    break

                self._update_jobs_status()
                yield from self._process_running_partitions_and_yield_completed_ones()
                self._wait_on_status_update()
            except Exception as exception:
                LOGGER.warning(
                    f"Caught exception that stops the processing of the jobs: {exception}. Traceback: {traceback.format_exc()}"
                )
                if self._is_breaking_exception(exception):
                    self._abort_all_running_jobs()
                    raise exception

                self._non_breaking_exceptions.append(exception)

        LOGGER.info(
            f"JobOrchestrator loop - Thread (Thread {threading.get_native_id()}, AsyncJobOrchestrator {self}) completed! Errors during creation were {self._non_breaking_exceptions}"
        )
        if self._non_breaking_exceptions:
            # We emitted traced message but we didn't break on non_breaking_exception. We still need to raise an exception so that the
            # call of `create_and_get_completed_partitions` knows that there was an issue with some partitions and the sync is incomplete.
            raise AirbyteTracedException(
                message="",
                internal_message="\n".join(
                    [
                        filter_secrets(exception.__repr__())
                        for exception in self._non_breaking_exceptions
                    ]
                ),
                failure_type=FailureType.config_error,
            )

    def _handle_non_breaking_error(self, exception: Exception) -> None:
        LOGGER.error(f"Failed to start the Job: {exception}, traceback: {traceback.format_exc()}")
        self._non_breaking_exceptions.append(exception)

    def _abort_all_running_jobs(self) -> None:
        for partition in self._running_partitions:
            for job in partition.jobs:
                if job.status() in self._RUNNING_ON_API_SIDE_STATUS:
                    self._abort_job(job, free_job_allocation=True)
                self._job_tracker.remove_job(job.api_job_id())

        self._running_partitions = []

    def _is_breaking_exception(self, exception: Exception) -> bool:
        return isinstance(exception, self._exceptions_to_break_on) or (
            isinstance(exception, AirbyteTracedException)
            and exception.failure_type == FailureType.config_error
        )

    def fetch_records(self, async_jobs: Iterable[AsyncJob]) -> Iterable[Mapping[str, Any]]:
        """
        Fetches records from the given jobs.

        Args:
            async_jobs Iterable[AsyncJob]: The list of AsyncJobs.

        Yields:
            Iterable[Mapping[str, Any]]: The fetched records from the jobs.
        """
        for job in async_jobs:
            yield from self._job_repository.fetch_records(job)
            self._job_repository.delete(job)
