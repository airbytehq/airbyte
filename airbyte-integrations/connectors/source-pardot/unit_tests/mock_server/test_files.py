# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any
from unittest import TestCase

from airbyte_cdk.models import AirbyteStreamStatus
from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import PardotRequestBuilder, login_request
from .response_builder import login_response, page_response
from .utils import read_stream, record_ids


_STREAM = "files"
_PATH = "v5/objects/files"
_FIELDS = (
    "id,name,folderId,campaignId,salesforceId,trackerDomainId,vanityUrl,vanityUrlPath,url,size,isTracked,"
    "bitlyIsPersonalized,bitlyShortUrl,createdAt,updatedAt,createdById,updatedById"
)


def _request() -> PardotRequestBuilder:
    return (
        PardotRequestBuilder.endpoint(_PATH)
        .with_query_param("limit", 1000)
        .with_query_param("fields", _FIELDS)
        .with_query_param("orderBy", "id ASC")
    )


def _next_page_request() -> PardotRequestBuilder:
    return PardotRequestBuilder.endpoint(_PATH).with_query_param("fields", _FIELDS).with_query_param("nextPageToken", "page-2")


def _file(file_id: int) -> dict[str, Any]:
    return {
        "id": file_id,
        "name": f"File {file_id}",
        "folderId": 7,
        "campaignId": 5,
        "trackerDomainId": 71,
        "vanityUrl": "https://go.example.com/whitepaper",
        "vanityUrlPath": "/whitepaper",
        "url": "https://go.example.com/l/1001/2026-02-01/whitepaper.pdf",
        "size": 204800,
        "isTracked": True,
        "bitlyIsPersonalized": False,
        "createdAt": "2026-02-01T08:00:00-08:00",
        "updatedAt": "2026-03-01T09:00:00-08:00",
        "createdById": 11,
        "updatedById": 11,
    }


class TestFilesStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request().build(),
            page_response([_file(number) for number in range(1, 1001)], next_page_url=_next_page_request().url()),
        )
        http_mocker.get(_next_page_request().build(), page_response([_file(1001), _file(1002)]))

        output = read_stream(_STREAM)

        assert record_ids(output) == list(range(1, 1003))
        assert output.records[0].record.data == _file(1)
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE

    @HttpMocker()
    def test_restarts_after_a_full_page_without_a_next_page_url(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(_request().build(), page_response([_file(number) for number in range(1, 1001)]))
        http_mocker.get(_request().with_query_param("idGreaterThan", 1000).build(), page_response([_file(1001)]))

        output = read_stream(_STREAM)

        assert record_ids(output) == list(range(1, 1002))
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
