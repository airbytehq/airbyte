# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase
from urllib.parse import urlencode

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest

from .request_builder import BASE_URL
from .response_builder import page_response, resource
from .utils import given_token, read_stream, record_ids


_STREAM = "compliance_requests"
_PATH = "/complianceRequests"
# `/complianceRequests` rejects `filter[updatedAt]` and `sort=updatedAt` with 400, so the stream sends neither.
_QUERY = {"count": "false", "page[size]": "1000"}


def _request() -> HttpRequest:
    return HttpRequest(f"{BASE_URL}{_PATH}", query_params=_QUERY)


def _compliance_request(resource_id: int) -> dict:
    return resource(
        resource_id,
        "complianceRequest",
        {
            "batchComplianceRequestUuid": "6f1c2b9e-3a5d-4e8f-9b0a-1c2d3e4f5a6b",
            "createdAt": "2024-01-02T03:04:05.000Z",
            "objectType": "Prospect",
            "pii": {"email": "ada@example.com"},
            "requestObjectId": "11",
            "requestType": "Delete",
            "requesterId": 7,
            "state": "done",
            "updatedAt": "2024-01-02T03:05:00.000Z",
            "uuid": "0b9c8d7e-6f5a-4b3c-2d1e-0f9a8b7c6d5e",
        },
        {"requester": {"data": {"type": "user", "id": 7}}},
    )


class TestComplianceRequestsStream(TestCase):
    @HttpMocker()
    def test_read_sends_no_sort_or_filter_and_flattens_relationships(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        http_mocker.get(_request(), page_response([_compliance_request(1)]))

        output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert [record.record.data for record in output.records] == [
            {
                "id": 1,
                "batchComplianceRequestUuid": "6f1c2b9e-3a5d-4e8f-9b0a-1c2d3e4f5a6b",
                "createdAt": "2024-01-02T03:04:05.000Z",
                "objectType": "Prospect",
                "pii": {"email": "ada@example.com"},
                "requestObjectId": "11",
                "requestType": "Delete",
                "requesterId": 7,
                "state": "done",
                "updatedAt": "2024-01-02T03:05:00.000Z",
                "uuid": "0b9c8d7e-6f5a-4b3c-2d1e-0f9a8b7c6d5e",
                "requester": [7],
            }
        ]

    @HttpMocker()
    def test_pagination_follows_links_next_until_it_is_absent(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        next_url = f"{BASE_URL}{_PATH}?{urlencode({**_QUERY, 'page[after]': 'eyJzcCI6bnVsbCwiaWQiOjF9'})}"
        http_mocker.get(_request(), page_response([_compliance_request(1)], next_url=next_url))
        http_mocker.get(HttpRequest(next_url), page_response([_compliance_request(2)]))

        output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert record_ids(output) == [1, 2]
