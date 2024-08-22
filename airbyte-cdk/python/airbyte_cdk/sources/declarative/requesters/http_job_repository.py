from typing import Iterable, Mapping, Any, Set

from airbyte_cdk import StreamSlice
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob
from airbyte_cdk.sources.declarative.async_job.repository import AsyncJobRepository


class AsyncHttpJobRepository(AsyncJobRepository):
    def start(self, stream_slice: StreamSlice) -> AsyncJob:
        raise NotImplementedError()

    def update_jobs_status(self, jobs: Set[AsyncJob]) -> None:
        pass

    def fetch_records(self, job: AsyncJob) -> Iterable[Mapping[str, Any]]:
        yield from []
