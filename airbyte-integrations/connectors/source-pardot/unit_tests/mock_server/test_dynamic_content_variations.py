# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any
from unittest import TestCase

from airbyte_cdk.models import AirbyteStreamStatus
from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import PardotRequestBuilder, login_request
from .response_builder import login_response, page_response
from .utils import read_stream, record_ids


_STREAM = "dynamic_content_variations"
_PATH = "v5/objects/dynamic-content-variations"
_FIELDS = "id,dynamicContentId,comparison,operator,value1,value2,content"


def _request() -> PardotRequestBuilder:
    return (
        PardotRequestBuilder.endpoint(_PATH)
        .with_query_param("limit", 1000)
        .with_query_param("fields", _FIELDS)
        .with_query_param("orderBy", "id ASC")
    )


def _next_page_request() -> PardotRequestBuilder:
    return PardotRequestBuilder.endpoint(_PATH).with_query_param("fields", _FIELDS).with_query_param("nextPageToken", "page-2")


def _variation(variation_id: int) -> dict[str, Any]:
    return {
        "id": variation_id,
        "dynamicContentId": 101,
        "comparison": "between 50 and 100",
        "operator": "between",
        "value1": "50",
        "value2": "100",
        "content": "<p>Thanks for being a customer.</p>",
    }


class TestDynamicContentVariationsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request().build(),
            page_response([_variation(number) for number in range(1, 1001)], next_page_url=_next_page_request().url()),
        )
        http_mocker.get(_next_page_request().build(), page_response([_variation(1001), _variation(1002)]))

        output = read_stream(_STREAM)

        assert record_ids(output) == list(range(1, 1003))
        assert output.records[0].record.data == _variation(1)
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE

    @HttpMocker()
    def test_restarts_after_a_full_page_without_a_next_page_url(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(_request().build(), page_response([_variation(number) for number in range(1, 1001)]))
        http_mocker.get(_request().with_query_param("idGreaterThan", 1000).build(), page_response([_variation(1001)]))

        output = read_stream(_STREAM)

        assert record_ids(output) == list(range(1, 1002))
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
