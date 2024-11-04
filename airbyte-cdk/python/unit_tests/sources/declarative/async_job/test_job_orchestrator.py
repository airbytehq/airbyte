# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
import sys
import threading
import time
from typing import Callable, List, Mapping, Optional, Set, Tuple
from unittest import TestCase, mock
from unittest.mock import MagicMock, Mock, call

import pytest
from airbyte_cdk import AirbyteTracedException, StreamSlice
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob, AsyncJobStatus
from airbyte_cdk.sources.declarative.async_job.job_orchestrator import AsyncJobOrchestrator, AsyncPartition
from airbyte_cdk.sources.declarative.async_job.job_tracker import JobTracker
from airbyte_cdk.sources.declarative.async_job.repository import AsyncJobRepository
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.http.http_client import MessageRepresentationAirbyteTracedErrors

_ANY_STREAM_SLICE = Mock()
_A_STREAM_SLICE = Mock()
_ANOTHER_STREAM_SLICE = Mock()
_ANY_RECORD = {"a record field": "a record value"}
_NO_JOB_LIMIT = sys.maxsize
_BUFFER = 10000  # this buffer allows us to be unconcerned with the number of times the update status is called


def _create_job(status: AsyncJobStatus = AsyncJobStatus.FAILED) -> AsyncJob:
    job = Mock(spec=AsyncJob)
    job.status.return_value = status
    return job


class AsyncPartitionTest(TestCase):
    def test_given_one_failed_job_when_status_then_return_failed(self) -> None:
        partition = AsyncPartition([_create_job(status) for status in AsyncJobStatus], _ANY_STREAM_SLICE)
        assert partition.status == AsyncJobStatus.FAILED

    def test_given_all_status_except_failed_when_status_then_return_timed_out(self) -> None:
        statuses = [status for status in AsyncJobStatus if status != AsyncJobStatus.FAILED]
        partition = AsyncPartition([_create_job(status) for status in statuses], _ANY_STREAM_SLICE)
        assert partition.status == AsyncJobStatus.TIMED_OUT

    def test_given_running_and_completed_jobs_when_status_then_return_running(self) -> None:
        partition = AsyncPartition([_create_job(AsyncJobStatus.RUNNING), _create_job(AsyncJobStatus.COMPLETED)], _ANY_STREAM_SLICE)
        assert partition.status == AsyncJobStatus.RUNNING

    def test_given_only_completed_jobs_when_status_then_return_running(self) -> None:
        partition = AsyncPartition([_create_job(AsyncJobStatus.COMPLETED) for _ in range(10)], _ANY_STREAM_SLICE)
        assert partition.status == AsyncJobStatus.COMPLETED


def _status_update_per_jobs(status_update_per_jobs: Mapping[AsyncJob, List[AsyncJobStatus]]) -> Callable[[set[AsyncJob]], None]:
    status_index_by_job = {job: 0 for job in status_update_per_jobs.keys()}

    def _update_status(jobs: Set[AsyncJob]) -> None:
        for job in jobs:
            status_index = status_index_by_job[job]
            job.update_status(status_update_per_jobs[job][status_index])
            status_index_by_job[job] += 1

    return _update_status


sleep_mock_target = "airbyte_cdk.sources.declarative.async_job.job_orchestrator.time.sleep"
_MAX_NUMBER_OF_ATTEMPTS = 3


class AsyncJobOrchestratorTest(TestCase):
    def setUp(self) -> None:
        self._job_repository = Mock(spec=AsyncJobRepository)
        self._message_repository = Mock(spec=MessageRepository)
        self._logger = Mock(spec=logging.Logger)

        self._job_for_a_slice = self._an_async_job("an api job id", _A_STREAM_SLICE)
        self._job_for_another_slice = self._an_async_job("another api job id", _ANOTHER_STREAM_SLICE)

    @mock.patch(sleep_mock_target)
    def test_when_create_and_get_completed_partitions_then_create_job_and_update_status_until_completed(self, mock_sleep: MagicMock) -> None:
        self._job_repository.start.return_value = self._job_for_a_slice
        status_updates = [AsyncJobStatus.RUNNING, AsyncJobStatus.RUNNING, AsyncJobStatus.COMPLETED]
        self._job_repository.update_jobs_status.side_effect = _status_update_per_jobs(
            {
                self._job_for_a_slice: status_updates
            }
        )
        orchestrator = self._orchestrator([_A_STREAM_SLICE])

        partitions = list(orchestrator.create_and_get_completed_partitions())

        assert len(partitions) == 1
        assert partitions[0].status == AsyncJobStatus.COMPLETED
        assert self._job_for_a_slice.update_status.mock_calls == [call(status) for status in status_updates]

    @mock.patch(sleep_mock_target)
    def test_given_one_job_still_running_when_create_and_get_completed_partitions_then_only_update_running_job_status(self, mock_sleep: MagicMock) -> None:
        self._job_repository.start.side_effect = [self._job_for_a_slice, self._job_for_another_slice]
        self._job_repository.update_jobs_status.side_effect = _status_update_per_jobs(
            {
                self._job_for_a_slice: [AsyncJobStatus.COMPLETED],
                self._job_for_another_slice: [AsyncJobStatus.RUNNING, AsyncJobStatus.COMPLETED],
            }
        )
        orchestrator = self._orchestrator([_A_STREAM_SLICE, _ANOTHER_STREAM_SLICE])

        list(orchestrator.create_and_get_completed_partitions())

        assert self._job_repository.update_jobs_status.mock_calls == [
            call({self._job_for_a_slice, self._job_for_another_slice}),
            call({self._job_for_another_slice}),
        ]

    @mock.patch(sleep_mock_target)
    def test_given_timeout_when_create_and_get_completed_partitions_then_free_budget_and_raise_exception(self, mock_sleep: MagicMock) -> None:
        job_tracker = JobTracker(1)
        self._job_repository.start.return_value = self._job_for_a_slice
        self._job_repository.update_jobs_status.side_effect = _status_update_per_jobs(
            {
                self._job_for_a_slice: [AsyncJobStatus.TIMED_OUT]
            }
        )
        orchestrator = self._orchestrator([_A_STREAM_SLICE], job_tracker)

        with pytest.raises(AirbyteTracedException):
            list(orchestrator.create_and_get_completed_partitions())
        assert job_tracker.try_to_get_intent()
        assert self._job_repository.start.call_args_list == [call(_A_STREAM_SLICE)] * _MAX_NUMBER_OF_ATTEMPTS

    @mock.patch(sleep_mock_target)
    def test_given_failure_when_create_and_get_completed_partitions_then_raise_exception(self, mock_sleep: MagicMock) -> None:
        self._job_repository.start.return_value = self._job_for_a_slice
        self._job_repository.update_jobs_status.side_effect = _status_update_per_jobs(
            {
                self._job_for_a_slice: [AsyncJobStatus.FAILED]
            }
        )
        orchestrator = self._orchestrator([_A_STREAM_SLICE])

        with pytest.raises(AirbyteTracedException):
            list(orchestrator.create_and_get_completed_partitions())
        assert self._job_repository.start.call_args_list == [call(_A_STREAM_SLICE)] * _MAX_NUMBER_OF_ATTEMPTS

    def test_when_fetch_records_then_yield_records_from_each_job(self) -> None:
        self._job_repository.fetch_records.return_value = [_ANY_RECORD]
        orchestrator = self._orchestrator([_A_STREAM_SLICE])
        first_job = _create_job()
        second_job = _create_job()
        partition = AsyncPartition([first_job, second_job], _A_STREAM_SLICE)

        records = list(orchestrator.fetch_records(partition))

        assert len(records) == 2
        assert self._job_repository.fetch_records.mock_calls == [call(first_job), call(second_job)]
        assert self._job_repository.delete.mock_calls == [call(first_job), call(second_job)]

    def _orchestrator(self, slices: List[StreamSlice], job_tracker: Optional[JobTracker] = None) -> AsyncJobOrchestrator:
        job_tracker = job_tracker if job_tracker else JobTracker(_NO_JOB_LIMIT)
        return AsyncJobOrchestrator(self._job_repository, slices, job_tracker, self._message_repository)

    def test_given_more_jobs_than_limit_when_create_and_get_completed_partitions_then_still_return_all_slices_and_free_job_budget(self) -> None:
        job_tracker = JobTracker(1)
        self._job_repository.start.side_effect = [self._job_for_a_slice, self._job_for_another_slice]
        self._job_repository.update_jobs_status.side_effect = _status_update_per_jobs(
            {
                self._job_for_a_slice: [AsyncJobStatus.COMPLETED],
                self._job_for_another_slice: [AsyncJobStatus.COMPLETED],
            }
        )
        orchestrator = self._orchestrator([self._job_for_a_slice.job_parameters(), self._job_for_another_slice.job_parameters()], job_tracker)

        partitions = list(orchestrator.create_and_get_completed_partitions())

        assert len(partitions) == 2
        assert job_tracker.try_to_get_intent()

    @mock.patch(sleep_mock_target)
    def test_given_exception_to_break_when_start_job_and_raise_this_exception_and_abort_jobs(self, mock_sleep: MagicMock) -> None:
        orchestrator = AsyncJobOrchestrator(
            self._job_repository,
            [_A_STREAM_SLICE, _ANOTHER_STREAM_SLICE],
            JobTracker(_NO_JOB_LIMIT),
            self._message_repository,
            exceptions_to_break_on=[ValueError],
        )
        self._job_repository.start.side_effect = [self._job_for_a_slice, ValueError("Something went wrong")]

        with pytest.raises(ValueError):
            # assert that orchestrator exits on expected error
            list(orchestrator.create_and_get_completed_partitions())
        assert len(orchestrator._job_tracker._jobs) == 0
        self._job_repository.abort.assert_called_once_with(self._job_for_a_slice)

    def test_given_traced_config_error_when_start_job_and_raise_this_exception_and_abort_jobs(self) -> None:
        """
        Since this is a config error, we assume the other jobs will fail for the same reasons.
        """
        job_tracker = JobTracker(1)
        self._job_repository.start.side_effect = MessageRepresentationAirbyteTracedErrors("Can't create job", failure_type=FailureType.config_error)

        orchestrator = AsyncJobOrchestrator(self._job_repository, [_A_STREAM_SLICE], job_tracker, self._message_repository, [ValueError])

        with pytest.raises(AirbyteTracedException):
            list(orchestrator.create_and_get_completed_partitions())

        assert job_tracker.try_to_get_intent()

    @mock.patch(sleep_mock_target)
    def test_given_exception_on_single_job_when_create_and_get_completed_partitions_then_return(self, mock_sleep: MagicMock) -> None:
        """
        We added this test because the initial logic of breaking the main loop we implemented (when `self._has_started_a_job and self._running_partitions`) was not enough in the case where there was only one slice and it would fail to start.
        """
        orchestrator = self._orchestrator([_A_STREAM_SLICE])
        self._job_repository.start.side_effect = ValueError

        with pytest.raises(AirbyteTracedException):
            # assert that orchestrator exits on expected error
            list(orchestrator.create_and_get_completed_partitions())

    @mock.patch(sleep_mock_target)
    def test_given_exception_when_start_job_and_skip_this_exception(self, mock_sleep: MagicMock) -> None:
        self._job_repository.start.side_effect = [
            AirbyteTracedException("Something went wrong. Expected error #1"),
            self._job_for_another_slice,
            AirbyteTracedException("Something went wrong. Expected error #2"),
            AirbyteTracedException("Something went wrong. Expected error #3"),
        ]
        self._job_repository.update_jobs_status.side_effect = _status_update_per_jobs(
            {
                self._job_for_a_slice: [AsyncJobStatus.COMPLETED],
                self._job_for_another_slice: [AsyncJobStatus.RUNNING, AsyncJobStatus.COMPLETED],
            }
        )
        orchestrator = self._orchestrator([_A_STREAM_SLICE, _ANOTHER_STREAM_SLICE])

        partitions, exception = self._accumulate_create_and_get_completed_partitions(orchestrator)

        assert len(partitions) == 1  # only _job_for_another_slice has succeeded
        assert self._message_repository.emit_message.call_count == 3  # one for each traced message
        assert exception.failure_type == FailureType.config_error  # type: ignore  # exception should be of type AirbyteTracedException

    @mock.patch(sleep_mock_target)
    def test_given_jobs_failed_more_than_max_attempts_when_create_and_get_completed_partitions_then_free_job_budget(self, mock_sleep: MagicMock) -> None:
        job_tracker = JobTracker(1)
        jobs = [self._an_async_job(str(i), _A_STREAM_SLICE) for i in range(_MAX_NUMBER_OF_ATTEMPTS)]
        self._job_repository.start.side_effect = jobs
        self._job_repository.update_jobs_status.side_effect = _status_update_per_jobs({job: [AsyncJobStatus.FAILED] for job in jobs})

        orchestrator = self._orchestrator([_A_STREAM_SLICE], job_tracker)

        with pytest.raises(AirbyteTracedException):
            list(orchestrator.create_and_get_completed_partitions())

        assert job_tracker.try_to_get_intent()

    def given_budget_already_taken_before_start_when_create_and_get_completed_partitions_then_wait_for_budget_to_be_freed(self) -> None:
        job_tracker = JobTracker(1)
        intent_to_free = job_tracker.try_to_get_intent()

        def wait_and_free_intent(_job_tracker: JobTracker, _intent_to_free: str) -> None:
            print("Waiting before freeing budget...")
            time.sleep(1)
            print("Waiting done, freeing budget!")
            _job_tracker.remove_job(_intent_to_free)
        self._job_repository.start.return_value = self._job_for_a_slice
        self._job_repository.update_jobs_status.side_effect = _status_update_per_jobs(
            {
                self._job_for_a_slice: [AsyncJobStatus.COMPLETED] * _BUFFER
            }
        )
        orchestrator = self._orchestrator([_A_STREAM_SLICE], job_tracker)

        threading.Thread(target=wait_and_free_intent, args=[job_tracker, intent_to_free]).start()
        partitions = list(orchestrator.create_and_get_completed_partitions())

        assert len(partitions) == 1

    def test_given_start_job_raise_when_create_and_get_completed_partitions_then_free_budget(self) -> None:
        job_tracker = JobTracker(1)
        self._job_repository.start.side_effect = ValueError("Can't create job")

        orchestrator = AsyncJobOrchestrator(self._job_repository, [_A_STREAM_SLICE], job_tracker, self._message_repository, [ValueError])

        with pytest.raises(Exception):
            list(orchestrator.create_and_get_completed_partitions())

        assert job_tracker.try_to_get_intent()

    def _mock_repository(self) -> None:
        self._job_repository = Mock(spec=AsyncJobRepository)

    def _an_async_job(self, job_id: str, stream_slice: StreamSlice) -> AsyncJob:
        return mock.Mock(wraps=AsyncJob(job_id, stream_slice))

    def _accumulate_create_and_get_completed_partitions(self, orchestrator: AsyncJobOrchestrator) -> Tuple[List[AsyncPartition], Optional[Exception]]:
        result = []
        try:
            for i in orchestrator.create_and_get_completed_partitions():
                result.append(i)
        except Exception as exception:
            return result, exception

        return result, None
