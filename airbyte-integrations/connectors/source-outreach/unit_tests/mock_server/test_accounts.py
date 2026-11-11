# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from airbyte_cdk.test.state_builder import StateBuilder

from .request_builder import OutreachRequestBuilder
from .response_builder import page_response, resource
from .utils import given_token, read_stream, record_ids, stream_state


_STREAM = "accounts"
_PATH = "/accounts"


def _request() -> OutreachRequestBuilder:
    return OutreachRequestBuilder.endpoint(_PATH)


def _account(resource_id: int, updated_at: str) -> dict:
    return resource(
        resource_id,
        "account",
        {
            "name": "Acme",
            "enrichable": False,
            "naicsCodes": ["541511"],
            "updatedAt": updated_at,
        },
        {
            "owner": {"data": {"type": "user", "id": 7}},
            "assignedUsers": {"data": [{"type": "user", "id": 7}, {"type": "user", "id": 8}]},
            "creator": {"data": None},
        },
    )


class TestAccountsStream(TestCase):
    @HttpMocker()
    def test_full_refresh_flattens_attributes_and_relationships(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        http_mocker.get(_request().build(), page_response([_account(1, "2024-01-02T03:04:05.000Z")]))

        output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert [record.record.data for record in output.records] == [
            {
                "id": 1,
                "name": "Acme",
                "enrichable": False,
                "naicsCodes": ["541511"],
                "updatedAt": "2024-01-02T03:04:05.000Z",
                "owner": [7],
                "assignedUsers": [7, 8],
            }
        ]

    @HttpMocker()
    def test_pagination_follows_links_next_until_it_is_absent(self, http_mocker: HttpMocker) -> None:
        # Every stream shares this paginator; each stream's test file repeats the check against its own path and page size.
        given_token(http_mocker)
        next_url = _request().next_page_url("eyJzcCI6InVwZGF0ZWRBdCJ9")
        http_mocker.get(_request().build(), page_response([_account(1, "2024-01-02T03:04:05.000Z")], next_url=next_url))
        http_mocker.get(HttpRequest(next_url), page_response([_account(2, "2024-01-03T03:04:05.000Z")]))

        output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert record_ids(output) == [1, 2]

    @HttpMocker()
    def test_incremental_first_sync_starts_at_start_date_and_emits_state(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        http_mocker.get(
            _request().build(),
            page_response([_account(1, "2024-01-02T03:04:05.000Z"), _account(2, "2024-01-03T03:04:05.123Z")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert not output.errors
        assert record_ids(output) == [1, 2]
        assert stream_state(output) == {"updatedAt": "2024-01-03T03:04:05.123Z"}

    @HttpMocker()
    def test_incremental_with_state_requests_from_the_saved_cursor(self, http_mocker: HttpMocker) -> None:
        state = StateBuilder().with_stream_state(_STREAM, {"updatedAt": "2024-01-03T03:04:05.123Z"}).build()
        given_token(http_mocker)
        http_mocker.get(
            _request().with_updated_since("2024-01-03T03:04:05.123Z").build(),
            page_response([_account(3, "2024-02-01T00:00:00.000Z")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental, state=state)

        assert not output.errors
        assert record_ids(output) == [3]
        assert stream_state(output) == {"updatedAt": "2024-02-01T00:00:00.000Z"}

    @HttpMocker()
    def test_incremental_stops_paging_at_a_record_older_than_the_state(self, http_mocker: HttpMocker) -> None:
        # `is_data_feed: true`: a record older than the saved cursor is dropped and ends the read, so the next page is
        # never requested. Every stream sets it; this test covers the shared behaviour.
        state = StateBuilder().with_stream_state(_STREAM, {"updatedAt": "2024-01-03T03:04:05.123Z"}).build()
        given_token(http_mocker)
        http_mocker.get(
            _request().with_updated_since("2024-01-03T03:04:05.123Z").build(),
            page_response(
                [_account(3, "2024-02-01T00:00:00.000Z"), _account(4, "2023-12-31T00:00:00.000Z")],
                next_url=_request().with_updated_since("2024-01-03T03:04:05.123Z").next_page_url("never-requested"),
            ),
        )

        output = read_stream(_STREAM, SyncMode.incremental, state=state)

        assert not output.errors
        assert record_ids(output) == [3]
        assert stream_state(output) == {"updatedAt": "2024-02-01T00:00:00.000Z"}
