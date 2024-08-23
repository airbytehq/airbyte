# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from typing import Any, Iterable, List, Mapping, Optional, Set, Tuple
from unittest import TestCase

from airbyte_cdk import AbstractSource, DeclarativeStream, SinglePartitionRouter, Stream, StreamSlice, init_logger
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob, AsyncJobStatus
from airbyte_cdk.sources.declarative.async_job.job_orchestrator import AsyncJobOrchestrator
from airbyte_cdk.sources.declarative.async_job.repository import AsyncJobRepository
from airbyte_cdk.sources.declarative.retrievers.async_retriever import AsyncRetriever
from airbyte_cdk.sources.declarative.schema import InlineSchemaLoader
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_protocol.models import ConnectorSpecification

_A_STREAM_NAME = "a_stream_name"


class MockAsyncJobRepository(AsyncJobRepository):

    def start(self, stream_slice: StreamSlice) -> AsyncJob:
        return AsyncJob("a_job_id")

    def update_jobs_status(self, jobs: Set[AsyncJob]) -> None:
        for job in jobs:
            job.update_status(AsyncJobStatus.COMPLETED)

    def fetch_records(self, job: AsyncJob) -> Iterable[Mapping[str, Any]]:
        yield from [{"record_field": 10}]


class MockSource(AbstractSource):

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        return True, None

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        return ConnectorSpecification(connectionSpecification={})

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            DeclarativeStream(
                retriever=AsyncRetriever(
                    stream_slicer=SinglePartitionRouter({}),
                    job_orchestrator_factory=lambda stream_slices: AsyncJobOrchestrator(MockAsyncJobRepository(), stream_slices, init_logger("airbyte.MockSource")),
                ),
                config={},
                parameters={},
                name=_A_STREAM_NAME,
                primary_key=[],
                schema_loader=InlineSchemaLoader({}, {}),
                stream_cursor_field="",  # the interface mentions that this is Optional but I get `'NoneType' object has no attribute 'eval'` by passing None
            )
        ]


class JobDeclarativeStreamTest(TestCase):
    _CONFIG = {}

    def setUp(self) -> None:
        self._source = MockSource()
        self._source.streams({})

    def test_godo(self) -> None:
        output = read(
            self._source,
            self._CONFIG,
            CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_A_STREAM_NAME)).build()
        )

        assert len(output.records) == 1
