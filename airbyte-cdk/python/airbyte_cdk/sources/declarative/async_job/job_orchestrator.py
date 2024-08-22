# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from typing import Iterable, Set

from airbyte_cdk import StreamSlice
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob

from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.declarative.async_job.repository import AsyncJobRepository


class AsyncPartition:
    """
    This bucket of api_jobs is a bit useless for this iteration but should become interesting when we will be able to split jobs
    """
    def __init__(self, jobs: Set[AsyncJob]) -> None:
        self._jobs = jobs

    @property
    def jobs(self) -> Set[AsyncJob]:
        return self._jobs

    # TODO def __repr__(self) -> str: for slice printing


class AsyncJobOrchestrator:
    _JOB_STATUS_UPDATE_SLEEP_DURATION = timedelta(seconds=30)

    def __init__(self, job_repository: AsyncJobRepository, slices: Iterable[StreamSlice]):
        self._slice_iterator = iter(slices)
        self._job_repository: AsyncJobRepository = job_repository

    def create_and_get_completed_partitions(self) -> Iterable[AsyncPartition]:
        raise NotImplementedError()

    def fetch_records(self, partition: AsyncPartition) -> Iterable[Record]:
        raise NotImplementedError()
