# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from typing import Any, Iterable, Mapping, Set

from airbyte_cdk import StreamSlice, Record
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob

from airbyte_cdk.sources.declarative.async_job.repository import AsyncJobRepository


class AsyncPartition:
    """
    This bucket of api_jobs is a bit useless for this iteration but should become interesting when we will be able to split jobs
    """
    def __init__(self, jobs: Set[AsyncJob], stream_slice: StreamSlice) -> None:
        self._jobs = jobs
        self._stream_slice = stream_slice

    @property
    def jobs(self) -> Set[AsyncJob]:
        return self._jobs

    @property
    def stream_slice(self) -> StreamSlice:
        return self._stream_slice

    # TODO def __repr__(self) -> str: for slice printing


class AsyncJobOrchestrator:
    _JOB_STATUS_UPDATE_SLEEP_DURATION = timedelta(seconds=30)

    def __init__(self, job_repository: AsyncJobRepository, slices: Iterable[StreamSlice]):
        self._slice_iterator = iter(slices)
        self._job_repository: AsyncJobRepository = job_repository

    def create_and_get_completed_partitions(self) -> Iterable[AsyncPartition]:
        """
        TODO Eventually, we need to cap the number of concurrent jobs. However, the first iteration is for sendgrid which only has one job
        """
        for _slice in self._slice_iterator:
            job = self._job_repository.start(_slice)
            yield AsyncPartition({job}, _slice)

    def fetch_records(self, partition: AsyncPartition) -> Iterable[Record]:
        for job in partition.jobs:
            for record in self._job_repository.fetch_records(job):
                yield Record(record, partition.stream_slice)
