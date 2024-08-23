# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Set

from airbyte_cdk import StreamSlice
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob
from airbyte_cdk.sources.declarative.async_job.repository import AsyncJobRepository
from airbyte_cdk.sources.declarative.requesters.requester import Requester


@dataclass
class AsyncHttpJobRepository(AsyncJobRepository):
    create_job_requester: Requester
    # TODO: update_job_requester: Requester
    # TODO: download_job_requester: Requester

    def start(self, stream_slice: StreamSlice) -> AsyncJob:
        response = self.create_job_requester.send_request(stream_slice=stream_slice)
        response.raise_for_status()
        job_id: str = response.json().get("id")
        return AsyncJob(api_job_id=job_id)

    def update_jobs_status(self, jobs: Set[AsyncJob]) -> None:
        raise NotImplementedError(f"Job Update Status Method called, but this method is dead end for now!")

    def fetch_records(self, job: AsyncJob) -> Iterable[Mapping[str, Any]]:
        yield from []
