from typing import Iterable, Mapping, Any, Set

from airbyte_cdk import StreamSlice
from airbyte_cdk.sources.declarative.async_job.job import Job
from airbyte_cdk.sources.declarative.async_job.repository import JobRepository


class HttpJobRepository(JobRepository):
    def start(self, stream_slice: StreamSlice) -> Job:
        raise NotImplementedError()

    def update_jobs_status(self, jobs: Set[Job]) -> None:
        pass

    def fetch_records(self, job: Job) -> Iterable[Mapping[str, Any]]:
        yield from []
