# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import json
from unittest import TestCase
from unittest.mock import Mock

import pytest
from airbyte_cdk.sources.declarative.async_job.status import AsyncJobStatus
from airbyte_cdk.sources.declarative.decoders import NoopDecoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors import DpathExtractor, RecordSelector, ResponseToFileExtractor
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.http_job_repository import AsyncHttpJobRepository
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators import DefaultPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.cursor_pagination_strategy import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

_ANY_CONFIG = {}
_ANY_SLICE = StreamSlice(partition={}, cursor_slice={})
_URL_BASE = "https://api.sendgrid.com/v3/"
_EXPORT_PATH = "marketing/contacts/exports"
_EXPORT_URL = f"{_URL_BASE}{_EXPORT_PATH}"
_A_JOB_ID = "a-job-id"
_ANOTHER_JOB_ID = "another-job-id"
_JOB_FIRST_URL = "https://job.result.api.com/1"
_JOB_SECOND_URL = "https://job.result.api.com/2"
_A_CSV_WITH_ONE_RECORD = """id,value
a_record_id,a_value
"""
_A_CURSOR_FOR_PAGINATION = "a-cursor-for-pagination"


class HttpJobRepositoryTest(TestCase):
    def setUp(self) -> None:
        message_repository = Mock()
        error_handler = DefaultErrorHandler(config=_ANY_CONFIG, parameters={})

        self._create_job_requester = HttpRequester(
            name="stream <name>: create_job",
            url_base=_URL_BASE,
            path=_EXPORT_PATH,
            error_handler=error_handler,
            http_method=HttpMethod.POST,
            config=_ANY_CONFIG,
            disable_retries=False,
            parameters={},
            message_repository=message_repository,
            use_cache=False,
            stream_response=False,
        )

        self._polling_job_requester = HttpRequester(
            name="stream <name>: polling",
            url_base=_URL_BASE,
            path=_EXPORT_PATH + "/{{stream_slice['create_job_response'].json()['id']}}",
            error_handler=error_handler,
            http_method=HttpMethod.GET,
            config=_ANY_CONFIG,
            disable_retries=False,
            parameters={},
            message_repository=message_repository,
            use_cache=False,
            stream_response=False,
        )

        self._download_retriever = SimpleRetriever(
            requester=HttpRequester(
                name="stream <name>: fetch_result",
                url_base="",
                path="{{stream_slice['url']}}",
                error_handler=error_handler,
                http_method=HttpMethod.GET,
                config=_ANY_CONFIG,
                disable_retries=False,
                parameters={},
                message_repository=message_repository,
                use_cache=False,
                stream_response=True,
            ),
            record_selector=RecordSelector(
                extractor=ResponseToFileExtractor(),
                record_filter=None,
                transformations=[],
                schema_normalization=TypeTransformer(TransformConfig.NoTransform),
                config=_ANY_CONFIG,
                parameters={},
            ),
            primary_key=None,
            name="any name",
            paginator=DefaultPaginator(
                decoder=NoopDecoder(),
                page_size_option=None,
                page_token_option=RequestOption(
                    field_name="locator",
                    inject_into=RequestOptionType.request_parameter,
                    parameters={},
                ),
                pagination_strategy=CursorPaginationStrategy(
                    cursor_value="{{ headers['Sforce-Locator'] }}",
                    decoder=NoopDecoder(),
                    config=_ANY_CONFIG,
                    parameters={},
                ),
                url_base=_URL_BASE,
                config=_ANY_CONFIG,
                parameters={},
            ),
            config=_ANY_CONFIG,
            parameters={},
        )

        self._repository = AsyncHttpJobRepository(
            creation_requester=self._create_job_requester,
            polling_requester=self._polling_job_requester,
            download_retriever=self._download_retriever,
            abort_requester=None,
            delete_requester=None,
            status_extractor=DpathExtractor(decoder=JsonDecoder(parameters={}), field_path=["status"], config={}, parameters={} or {}),
            status_mapping={
                "ready": AsyncJobStatus.COMPLETED,
                "failure": AsyncJobStatus.FAILED,
                "pending": AsyncJobStatus.RUNNING,
            },
            urls_extractor=DpathExtractor(decoder=JsonDecoder(parameters={}), field_path=["urls"], config={}, parameters={} or {}),
        )

        self._http_mocker = HttpMocker()
        self._http_mocker.__enter__()

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    def test_given_different_statuses_when_update_jobs_status_then_update_status_properly(self) -> None:
        self._mock_create_response(_A_JOB_ID)
        self._http_mocker.get(
            HttpRequest(url=f"{_EXPORT_URL}/{_A_JOB_ID}"),
            [
                HttpResponse(body=json.dumps({"id": _A_JOB_ID, "status": "pending"})),
                HttpResponse(body=json.dumps({"id": _A_JOB_ID, "status": "failure"})),
                HttpResponse(body=json.dumps({"id": _A_JOB_ID, "status": "ready"})),
            ]
        )
        job = self._repository.start(_ANY_SLICE)

        self._repository.update_jobs_status([job])
        assert job.status() == AsyncJobStatus.RUNNING
        self._repository.update_jobs_status([job])
        assert job.status() == AsyncJobStatus.FAILED
        self._repository.update_jobs_status([job])
        assert job.status() == AsyncJobStatus.COMPLETED

    def test_given_unknown_status_when_update_jobs_status_then_raise_error(self) -> None:
        self._mock_create_response(_A_JOB_ID)
        self._http_mocker.get(
            HttpRequest(url=f"{_EXPORT_URL}/{_A_JOB_ID}"),
            HttpResponse(body=json.dumps({"id": _A_JOB_ID, "status": "invalid_status"})),
        )
        job = self._repository.start(_ANY_SLICE)

        with pytest.raises(ValueError):
            self._repository.update_jobs_status([job])

    def test_given_multiple_jobs_when_update_jobs_status_then_all_the_jobs_are_updated(self) -> None:
        self._mock_create_response(_A_JOB_ID)
        self._http_mocker.get(
            HttpRequest(url=f"{_EXPORT_URL}/{_A_JOB_ID}"),
            HttpResponse(body=json.dumps({"id": _A_JOB_ID, "status": "ready"})),
        )
        self._mock_create_response(_ANOTHER_JOB_ID)
        self._http_mocker.get(
            HttpRequest(url=f"{_EXPORT_URL}/{_ANOTHER_JOB_ID}"),
            HttpResponse(body=json.dumps({"id": _A_JOB_ID, "status": "ready"})),
        )
        a_job = self._repository.start(_ANY_SLICE)
        another_job = self._repository.start(_ANY_SLICE)

        self._repository.update_jobs_status([a_job, another_job])

        assert a_job.status() == AsyncJobStatus.COMPLETED
        assert another_job.status() == AsyncJobStatus.COMPLETED

    def test_given_pagination_when_fetch_records_then_yield_records_from_all_pages(self) -> None:
        self._mock_create_response(_A_JOB_ID)
        self._http_mocker.get(
            HttpRequest(url=f"{_EXPORT_URL}/{_A_JOB_ID}"),
            HttpResponse(body=json.dumps({
                "id": _A_JOB_ID,
                "status": "ready",
                "urls": [_JOB_FIRST_URL]
            }))
        )
        self._http_mocker.get(
            HttpRequest(url=_JOB_FIRST_URL),
            HttpResponse(body=_A_CSV_WITH_ONE_RECORD, headers={"Sforce-Locator": _A_CURSOR_FOR_PAGINATION}),
        )
        self._http_mocker.get(
            HttpRequest(url=_JOB_FIRST_URL, query_params={"locator": _A_CURSOR_FOR_PAGINATION}),
            HttpResponse(body=_A_CSV_WITH_ONE_RECORD),
        )

        job = self._repository.start(_ANY_SLICE)
        self._repository.update_jobs_status([job])
        records = list(self._repository.fetch_records(job))

        assert len(records) == 2

    def test_given_multiple_urls_when_fetch_records_then_fetch_from_multiple_urls(self) -> None:
        self._mock_create_response(_A_JOB_ID)
        self._http_mocker.get(
            HttpRequest(url=f"{_EXPORT_URL}/{_A_JOB_ID}"),
            HttpResponse(body=json.dumps({
                "id": _A_JOB_ID,
                "status": "ready",
                "urls": [
                    _JOB_FIRST_URL,
                    _JOB_SECOND_URL,
                ]
            }))
        )
        self._http_mocker.get(
            HttpRequest(url=_JOB_FIRST_URL),
            HttpResponse(body=_A_CSV_WITH_ONE_RECORD),
        )
        self._http_mocker.get(
            HttpRequest(url=_JOB_SECOND_URL),
            HttpResponse(body=_A_CSV_WITH_ONE_RECORD),
        )

        job = self._repository.start(_ANY_SLICE)
        self._repository.update_jobs_status([job])
        records = list(self._repository.fetch_records(job))

        assert len(records) == 2

    def _mock_create_response(self, job_id: str) -> None:
        self._http_mocker.post(
            HttpRequest(url=_EXPORT_URL),
            HttpResponse(body=json.dumps({"id": job_id})),
        )
