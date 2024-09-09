# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from typing import Callable, List, Mapping, Set
from unittest import TestCase, mock
from unittest.mock import MagicMock, Mock, call

import pytest
from airbyte_cdk import AirbyteTracedException, StreamSlice
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob, AsyncJobStatus
from airbyte_cdk.sources.declarative.async_job.job_orchestrator import AsyncJobOrchestrator, AsyncPartition
from airbyte_cdk.sources.declarative.async_job.repository import AsyncJobRepository

_ANY_STREAM_SLICE = Mock()
_A_STREAM_SLICE = Mock()
_ANOTHER_STREAM_SLICE = Mock()
_ANY_RECORD = {"a record field": "a record value"}


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


class AsyncJobOrchestratorTest(TestCase):
    def setUp(self) -> None:
        self._job_repository = Mock(spec=AsyncJobRepository)
        self._logger = Mock(spec=logging.Logger)

        self._job_for_a_slice = mock.Mock(wraps=AsyncJob("an api job id", _A_STREAM_SLICE))
        self._job_for_another_slice = mock.Mock(wraps=AsyncJob("another api job id", _ANOTHER_STREAM_SLICE))

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
    def test_given_timeout_when_create_and_get_completed_partitions_then_raise_exception(self, mock_sleep: MagicMock) -> None:
        self._job_repository.start.return_value = self._job_for_a_slice
        self._job_repository.update_jobs_status.side_effect = _status_update_per_jobs(
            {
                self._job_for_a_slice: [AsyncJobStatus.TIMED_OUT]
            }
        )
        orchestrator = self._orchestrator([_A_STREAM_SLICE])

        with pytest.raises(AirbyteTracedException):
            list(orchestrator.create_and_get_completed_partitions())
        assert self._job_repository.start.call_args_list == [call(_A_STREAM_SLICE)] * 4

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
        assert self._job_repository.start.call_args_list == [call(_A_STREAM_SLICE)] * 4

    def test_when_fetch_records_then_yield_records_from_each_job(self) -> None:
        self._job_repository.fetch_records.return_value = [_ANY_RECORD]
        orchestrator = self._orchestrator([_A_STREAM_SLICE])
        first_job = _create_job()
        second_job = _create_job()
        partition = AsyncPartition([first_job, second_job], _A_STREAM_SLICE)

        records = list(orchestrator.fetch_records(partition))

        assert len(records) == 2
        assert self._job_repository.fetch_records.mock_calls == [call(first_job), call(second_job)]

    def _orchestrator(self, slices: List[StreamSlice]) -> AsyncJobOrchestrator:
        return AsyncJobOrchestrator(self._job_repository, slices)
