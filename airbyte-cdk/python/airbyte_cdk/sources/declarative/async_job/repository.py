# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Set

from airbyte_cdk import StreamSlice
from airbyte_cdk.sources.declarative.async_job.job import Job


class JobRepository(ABC):

    @abstractmethod
    def start(self, stream_slice: StreamSlice) -> Job:
        pass

    @abstractmethod
    def update_jobs_status(self, jobs: Set[Job]) -> None:
        pass

    @abstractmethod
    def fetch_records(self, job: Job) -> Iterable[Mapping[str, Any]]:
        pass

