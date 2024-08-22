# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import time
from datetime import timedelta
from typing import Iterable, Set

from airbyte_cdk import StreamSlice
from airbyte_cdk.sources.declarative.async_job.job import Job

from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.job.job_dao import JobRepository


class AsyncPartition:
    """
    This bucket of api_jobs is a bit useless for this iteration but should become interesting when we will be able to split jobs
    """
    def __init__(self, jobs: Set[Job]) -> None:
        self._jobs = jobs

    @property
    def jobs(self) -> Set[Job]:
        return self._jobs

    # TODO def __repr__(self) -> str: for slice printing


class JobOrchestrator:
    _JOB_STATUS_UPDATE_SLEEP_DURATION = timedelta(seconds=30)

    def __init__(self, job_repository: JobRepository, slices: Iterable[StreamSlice]):
        self._slice_iterator = iter(slices)
        self._job_repository: JobRepository = job_repository

    def create_and_get_completed_partitions(self) -> Iterable[AsyncPartition]:
        raise NotImplementedError()

    def fetch_records(self, partition: AsyncPartition) -> Iterable[Record]:
        raise NotImplementedError()
