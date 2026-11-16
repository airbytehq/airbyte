# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase
from urllib.parse import urlencode

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest

from .request_builder import BASE_URL
from .response_builder import page_response, resource
from .utils import given_token, read_stream, record_ids


_STREAM = "recipients"
_PATH = "/recipients"
# `/recipients` rejects `filter[updatedAt]` and `sort=updatedAt` with 400, so the stream sends neither.
_QUERY = {"count": "false", "page[size]": "1000"}


def _request() -> HttpRequest:
    return HttpRequest(f"{BASE_URL}{_PATH}", query_params=_QUERY)


def _recipient(resource_id: int) -> dict:
    return resource(
        resource_id,
        "recipient",
        {
            "createdAt": "2021-11-10T13:37:37.000Z",
            "emailHash": "bacb0453ec521105740de044234b0ba1",
            "primary": False,
            "recipientType": "cc",
            "updatedAt": "2021-11-10T13:37:37.000Z",
            "value": '"Ada Lovelace" <ada@example.com>',
        },
        {"prospect": {"data": {"type": "prospect", "id": 7}}, "user": {"data": None}},
    )


class TestRecipientsStream(TestCase):
    @HttpMocker()
    def test_read_sends_no_sort_or_filter_and_flattens_relationships(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        http_mocker.get(_request(), page_response([_recipient(4)]))

        output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert [record.record.data for record in output.records] == [
            {
                "id": 4,
                "createdAt": "2021-11-10T13:37:37.000Z",
                "emailHash": "bacb0453ec521105740de044234b0ba1",
                "primary": False,
                "recipientType": "cc",
                "updatedAt": "2021-11-10T13:37:37.000Z",
                "value": '"Ada Lovelace" <ada@example.com>',
                "prospect": [7],
            }
        ]

    @HttpMocker()
    def test_pagination_follows_links_next_until_it_is_absent(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        next_url = f"{BASE_URL}{_PATH}?{urlencode({**_QUERY, 'page[after]': 'eyJzcCI6bnVsbCwiaWQiOjR9'})}"
        http_mocker.get(_request(), page_response([_recipient(4)], next_url=next_url))
        http_mocker.get(HttpRequest(next_url), page_response([_recipient(5)]))

        output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert record_ids(output) == [4, 5]
