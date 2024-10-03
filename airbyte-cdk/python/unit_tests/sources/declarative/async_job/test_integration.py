# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import logging
from typing import Any, Iterable, List, Mapping, Optional, Set, Tuple
from unittest import TestCase, mock

from airbyte_cdk import AbstractSource, DeclarativeStream, SinglePartitionRouter, Stream, StreamSlice
from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob
from airbyte_cdk.sources.declarative.async_job.job_orchestrator import AsyncJobOrchestrator
from airbyte_cdk.sources.declarative.async_job.job_tracker import JobTracker
from airbyte_cdk.sources.declarative.async_job.repository import AsyncJobRepository
from airbyte_cdk.sources.declarative.async_job.status import AsyncJobStatus
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector
from airbyte_cdk.sources.declarative.retrievers.async_retriever import AsyncRetriever
from airbyte_cdk.sources.declarative.schema import InlineSchemaLoader
from airbyte_cdk.sources.declarative.stream_slicers import StreamSlicer
from airbyte_cdk.sources.message import NoopMessageRepository
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read

_A_STREAM_NAME = "a_stream_name"
_EXTRACTOR_NOT_USED: RecordExtractor = None  # type: ignore  # the extractor should not be used. If it is the case, there is an issue that needs fixing
_NO_LIMIT = 10000


class MockAsyncJobRepository(AsyncJobRepository):

    def start(self, stream_slice: StreamSlice) -> AsyncJob:
        return AsyncJob("a_job_id", StreamSlice(partition={}, cursor_slice={}))

    def update_jobs_status(self, jobs: Set[AsyncJob]) -> None:
        for job in jobs:
            job.update_status(AsyncJobStatus.COMPLETED)

    def fetch_records(self, job: AsyncJob) -> Iterable[Mapping[str, Any]]:
        yield from [{"record_field": 10}]

    def abort(self, job: AsyncJob) -> None:
        pass

    def delete(self, job: AsyncJob) -> None:
        pass


class MockSource(AbstractSource):

    def __init__(self, stream_slicer: Optional[StreamSlicer] = None) -> None:
        self._stream_slicer = SinglePartitionRouter({}) if stream_slicer is None else stream_slicer
        self._message_repository = NoopMessageRepository()

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        return True, None

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        return ConnectorSpecification(connectionSpecification={})

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        noop_record_selector = RecordSelector(
            extractor=_EXTRACTOR_NOT_USED,
            config={},
            parameters={},
            schema_normalization=TypeTransformer(TransformConfig.NoTransform),
            record_filter=None,
            transformations=[]
        )
        return [
            DeclarativeStream(
                retriever=AsyncRetriever(
                    config={},
                    parameters={},
                    record_selector=noop_record_selector,
                    stream_slicer=self._stream_slicer,
                    job_orchestrator_factory=lambda stream_slices: AsyncJobOrchestrator(
                        MockAsyncJobRepository(), stream_slices, JobTracker(_NO_LIMIT), self._message_repository,
                    ),
                ),
                config={},
                parameters={},
                name=_A_STREAM_NAME,
                primary_key=["id"],
                schema_loader=InlineSchemaLoader({}, {}),
                # the interface mentions that this is Optional,
                # but I get `'NoneType' object has no attribute 'eval'` by passing None
                stream_cursor_field="",
            )
        ]


class JobDeclarativeStreamTest(TestCase):
    _CONFIG: Mapping[str, Any] = {}

    def setUp(self) -> None:
        self._stream_slicer = mock.Mock(wraps=SinglePartitionRouter({}))
        self._source = MockSource(self._stream_slicer)
        self._source.streams({})

    def test_when_read_then_return_records_from_repository(self) -> None:
        output = read(
            self._source,
            self._CONFIG,
            CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_A_STREAM_NAME)).build()
        )

        assert len(output.records) == 1

    def test_when_read_then_call_stream_slices_only_once(self) -> None:
        """
        As generating stream slices is very expensive, we want to ensure that during a read, it is only called once.
        """
        output = read(
            self._source,
            self._CONFIG,
            CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_A_STREAM_NAME)).build()
        )

        assert not output.errors
        assert self._stream_slicer.stream_slices.call_count == 1
