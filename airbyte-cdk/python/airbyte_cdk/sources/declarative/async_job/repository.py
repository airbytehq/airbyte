# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from abc import abstractmethod
from typing import Any, Iterable, Mapping, Set

from airbyte_cdk import StreamSlice
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob


class AsyncJobRepository:
    @abstractmethod
    def start(self, stream_slice: StreamSlice) -> AsyncJob:
        pass

    @abstractmethod
    def update_jobs_status(self, jobs: Set[AsyncJob]) -> None:
        pass

    @abstractmethod
    def fetch_records(self, job: AsyncJob) -> Iterable[Mapping[str, Any]]:
        pass

    @abstractmethod
    def abort(self, job: AsyncJob) -> None:
        """
        Called when we need to stop on the API side. This method can raise NotImplementedError as not all the APIs will support aborting
        jobs.
        """
        raise NotImplementedError("Either the API or the AsyncJobRepository implementation do not support aborting jobs")

    @abstractmethod
    def delete(self, job: AsyncJob) -> None:
        pass
