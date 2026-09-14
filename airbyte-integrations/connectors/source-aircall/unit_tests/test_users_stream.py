# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `users` stream migration to the Aircall User V2 API.

Aircall sunsets `GET /v1/users` on 2026-09-30. The stream now reads from
`https://api.aircall.io/v2/users` (same `{"users": [...], "meta": {...}}`
envelope) and paginates with 1-indexed `page`/`per_page` query params, matching
the V2 API where page 1 is the first page. These tests pin the exact request
sequence so a regression to the V1 host or to 0-indexed pagination fails.
"""

import json
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_STREAM_NAME = "users"
_V2_USERS_URL = "https://api.aircall.io/v2/users"

_CONFIG = {
    "api_id": "id",
    "api_token": "token",
    "start_date": "2022-03-01T00:00:00.000Z",
}

_FIRST_PAGE_REQUEST = HttpRequest(_V2_USERS_URL, query_params={"per_page": "50"})
_SECOND_PAGE_REQUEST = HttpRequest(_V2_USERS_URL, query_params={"per_page": "50", "page": "2"})


def _user(user_id: int) -> Dict[str, Any]:
    return {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@airbyte.io",
        "direct_link": f"https://api.aircall.io/v2/users/{user_id}",
        "language": "en-US",
        "created_at": "2025-09-15T12:14:21.000Z",
        "time_zone": "Etc/UTC",
        "state": "always_opened",
        "wrap_up_time": 0,
        "extension": "001",
        "availability_status": "available",
        "available": False,
        "default_number_id": None,
        "substatus": "always_opened",
    }


def _users_response(users: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(
        body=json.dumps({"users": users, "meta": {"count": len(users), "total": 999, "current_page": 1}}),
        status_code=200,
    )


def _read_users() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)


class UsersStreamTest(TestCase):
    @HttpMocker()
    def test_users_stream_reads_from_v2_endpoint_with_pagination(self, http_mocker: HttpMocker):
        http_mocker.get(_FIRST_PAGE_REQUEST, _users_response([_user(i) for i in range(1, 51)]))
        http_mocker.get(_SECOND_PAGE_REQUEST, _users_response([_user(51)]))

        output = _read_users()

        assert len(output.records) == 51
        assert [record.record.data["id"] for record in output.records] == list(range(1, 52))
        for record in output.records:
            assert record.record.data["direct_link"].startswith("https://api.aircall.io/v2/")
        # The first request carries no `page` param and the second carries
        # `page=2`, so `start_from_page: 1` on the PageIncrement is load-bearing.
        http_mocker.assert_number_of_calls(_FIRST_PAGE_REQUEST, 1)
        http_mocker.assert_number_of_calls(_SECOND_PAGE_REQUEST, 1)

    @HttpMocker()
    def test_users_stream_stops_after_partial_page(self, http_mocker: HttpMocker):
        http_mocker.get(_FIRST_PAGE_REQUEST, _users_response([_user(i) for i in range(1, 4)]))

        output = _read_users()

        assert len(output.records) == 3
        http_mocker.assert_number_of_calls(_FIRST_PAGE_REQUEST, 1)

    @HttpMocker()
    def test_users_stream_does_not_target_v1_endpoint(self, http_mocker: HttpMocker):
        # Nothing is mocked, so any request the stream makes fails with
        # NoMockAddress. The error log names the URL it attempted, which proves
        # the stream targets the V2 endpoint (and no longer V1).
        output = _read_users()

        assert len(output.records) == 0
        assert output.is_in_logs("api.aircall.io/v2/users")
        assert output.is_not_in_logs("api.aircall.io/v1/users")
